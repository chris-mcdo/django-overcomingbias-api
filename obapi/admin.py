from django.contrib import admin, messages
from django.contrib.admin.helpers import Fieldset
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.db import IntegrityError
from django.forms import BaseInlineFormSet
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import ngettext

from obapi import utils
from obapi.exceptions import APICallError
from obapi.forms import (
    AddOBContentItemForm,
    AddSpotifyContentItemForm,
    AddYoutubeContentItemForm,
)
from obapi.models import (
    Author,
    AuthorAlias,
    ContentItem,
    Idea,
    IdeaAlias,
    OBContentItem,
    SpotifyContentItem,
    Tag,
    TagAlias,
    Topic,
    TopicAlias,
    YoutubeContentItem,
)
from obapi.models.classifiers import ExternalLink

# Inlines
# https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#inlinemodeladmin-objects


class AliasInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # Ensure aliases differ from the name
        name_slug = utils.to_slug(self.data["name"])
        forms_to_delete = self.deleted_forms
        valid_forms = [
            form
            for form in self.forms
            if form.is_valid() and form not in forms_to_delete
        ]

        for form in valid_forms:
            # If an alias matches the current name, mark its form for deletion
            alias = form.cleaned_data["text"]
            if alias == name_slug:
                form.cleaned_data["DELETE"] = True


class AliasInline(admin.TabularInline):
    extra = 0
    formset = AliasInlineFormset

    def get_queryset(self, request):
        return super().get_queryset(request).filter(protected=False)


class AuthorAliasInline(AliasInline):
    model = AuthorAlias


class IdeaAliasInline(AliasInline):
    model = IdeaAlias


class TopicAliasInline(AliasInline):
    model = TopicAlias


class TagAliasInline(AliasInline):
    model = TagAlias


class ContentItemInline(admin.StackedInline):
    model = ContentItem.external_links.through
    extra = 0

    autocomplete_fields = ("contentitem",)


# Admin actions
# https://docs.djangoproject.com/en/4.0/ref/contrib/admin/actions/


@admin.action(description="Merge objects", permissions=["change"])
def merge_aliased_objects(modeladmin, request, queryset):
    """Merge multiple objects and their aliases."""
    if (object_count := queryset.count()) < 2:
        modeladmin.message_user(
            request,
            "Two or more items must be selected to merge. No items have been changed.",
            messages.WARNING,
        )
        return

    new_object = queryset.merge_objects()

    modeladmin.message_user(
        request,
        f"{object_count} objects merged into {new_object.name}.",
        messages.SUCCESS,
    )


def convert_aliased_objects(modeladmin, request, queryset, model):
    # Track errors and successes
    err_count = success_count = 0

    # Attempt to convert each object in the queryset
    for obj in queryset:
        try:
            obj.convert_object(model)
            success_count = success_count + 1
        except IntegrityError:
            err_count = err_count + 1
            pass

    # Message user about errors and successes
    if success_count > 0:
        modeladmin.message_user(
            request,
            f"{success_count} {model._meta.verbose_name_plural} successfully created",
            messages.SUCCESS,
        )
    if err_count > 0:
        modeladmin.message_user(
            request,
            f"{err_count} {model._meta.verbose_name_plural} could not be created",
            messages.WARNING,
        )


@admin.action(description="Convert selected items to Authors")
def convert_to_authors(modeladmin, request, queryset):
    convert_aliased_objects(modeladmin, request, queryset, Author)


@admin.action(description="Convert selected items to Ideas")
def convert_to_ideas(modeladmin, request, queryset):
    convert_aliased_objects(modeladmin, request, queryset, Idea)


@admin.action(description="Convert selected items to Topics")
def convert_to_topics(modeladmin, request, queryset):
    convert_aliased_objects(modeladmin, request, queryset, Topic)


@admin.action(description="Convert selected items to Tags")
def convert_to_tags(modeladmin, request, queryset):
    convert_aliased_objects(modeladmin, request, queryset, Tag)


# Model Admins
# https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#modeladmin-objects


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    inlines = [AuthorAliasInline]
    actions = [
        merge_aliased_objects,
        convert_to_ideas,
        convert_to_topics,
        convert_to_tags,
    ]
    search_fields = ("name",)


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    inlines = [IdeaAliasInline]
    actions = [
        merge_aliased_objects,
        convert_to_authors,
        convert_to_topics,
        convert_to_tags,
    ]
    search_fields = ("name",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    inlines = [TopicAliasInline]
    actions = [
        merge_aliased_objects,
        convert_to_authors,
        convert_to_ideas,
        convert_to_tags,
    ]
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = [TagAliasInline]
    actions = [
        merge_aliased_objects,
        convert_to_authors,
        convert_to_ideas,
        convert_to_topics,
    ]
    search_fields = ("name",)


@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    inlines = [
        ContentItemInline,
    ]
    exclude = ("external_links",)
    search_fields = ("url",)
    actions = ("delete_unreferenced_links",)

    @admin.action(description="Delete unreferenced links", permissions=["delete"])
    def delete_unreferenced_links(self, request, queryset):
        delete_count, details = queryset.filter(content__isnull=True).delete()
        self.message_user(
            request,
            f"{delete_count} links deleted",
            messages.INFO,
        )


class ContentItemAdminTemplate(admin.ModelAdmin):
    add_form_template = "admin/obapi/add_form.html"
    AddForm = None  # override in subclasses

    actions = ["update_selected_items", "internalize_links"]

    readonly_fields = ("create_timestamp", "update_timestamp", "download_timestamp")

    search_fields = ("title",)

    autocomplete_fields = (
        "authors",
        "ideas",
        "topics",
        "tags",
        "external_links",
        "internal_links",
    )

    def add_view(self, request, form_url="", extra_context=None):
        if not self.has_add_permission(request):
            raise PermissionDenied
        if request.method == "POST":
            form = self.AddForm(request.POST)
            if form.is_valid():
                id_field = next(iter(form.fields.values())).label
                message_if_error = (
                    f"Could not retrieve item. Please check the {id_field} is valid."
                )
                try:
                    item = form.save()
                except APICallError:
                    item = None
                except IntegrityError:
                    item = None
                    message_if_error = "The specified item already exists."
                if item is not None:
                    change_message = f"Created item {item}."
                    self.log_addition(request, item, change_message)
                    return self.response_add(request, item)

                self.message_user(
                    request,
                    message_if_error,
                    messages.ERROR,
                )

        else:
            form = self.AddForm()

        opts = self.model._meta
        fieldset = Fieldset(form, fields=form.fields, model_admin=self)
        context = {
            **self.admin_site.each_context(request),
            "title": f"Add {self.model._meta.verbose_name}",
            "fieldset": fieldset,
            "media": self.media,
            "errors": form.errors,
            "add": True,
            "has_view_permission": self.has_view_permission(request, None),
            "has_add_permission": self.has_add_permission(request),
            "has_change_permission": self.has_change_permission(request, None),
            "has_delete_permission": self.has_delete_permission(request, None),
            "opts": opts,
            "app_label": opts.app_label,
            **(extra_context or {}),
        }
        request.current_app = self.admin_site.name
        form_template = self.add_form_template
        return TemplateResponse(request, form_template, context)

    @admin.action(description="Update selected items", permissions=["change"])
    def update_selected_items(self, request, queryset):
        queryset.update_items()

    @admin.action(description="Internalize links", permissions=["change"])
    def internalize_links(self, request, queryset):
        try:
            for item in queryset:
                item.internalize_links(clear=False)
        except IntegrityError:
            self.message_user(
                request, "Error when internalizing links.", messages.ERROR
            )
        else:
            self.message_user(
                request, "Links internalized successfully.", messages.SUCCESS
            )


@admin.register(ContentItem)
class ContentItemAdmin(ContentItemAdminTemplate):
    # Revert to standard add view
    def add_view(self, request, form_url="", extra_context=None):
        return self.changeform_view(request, None, form_url, extra_context)

    @admin.action(description="Update selected items", permissions=["change"])
    def update_selected_items(self, request, queryset):
        for model in (YoutubeContentItem, SpotifyContentItem, OBContentItem):
            model.objects.filter(
                pk__in=queryset.select_subclasses(model)
            ).update_items()


@admin.register(YoutubeContentItem)
class YoutubeContentItemAdmin(ContentItemAdminTemplate):
    AddForm = AddYoutubeContentItemForm


@admin.register(SpotifyContentItem)
class SpotifyContentItemAdmin(ContentItemAdminTemplate):
    AddForm = AddSpotifyContentItemForm


@admin.register(OBContentItem)
class OBContentItemAdmin(ContentItemAdminTemplate):
    AddForm = AddOBContentItemForm

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "update/",
                self.admin_site.admin_view(self.update_view),
                name="obapi_obcontentitem_update",
            )
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context.update(has_change_permission=self.has_change_permission(request))
        return super().changelist_view(request, extra_context)

    def update_view(self, request):
        """View to update existing OB content items.

        Either downloads all new posts ("pull") or updates all edited posts ("sync").

        Works by (1) performing the requested operation, (2) logging the results and
        messaging the user, and (3) redirecting to list / index page.
        """
        # Accept POST requests only
        if request.method != "POST":
            raise Http404

        if "_pull" in request.POST:
            # Check permissions
            if not self.has_add_permission(request):
                raise PermissionDenied
            # Pull items
            created_items = OBContentItem.objects.download_new_items()
            # Messaging & logging
            changecount = len(created_items)
            changetype = "created"
            for item in created_items:
                self.log_addition(request, item, f"Created item {item}.")
        elif "_sync" in request.POST:
            # Check permissions
            if not self.has_change_permission(request):
                raise PermissionDenied
            # Sync items
            updated_items = OBContentItem.objects.update_edited_items()
            # Messaging & logging
            changecount = len(updated_items)
            changetype = "updated"
            for item in updated_items:
                self.log_change(request, item, f"Updated item {item}.")
        else:
            raise SuspiciousOperation

        # Send message
        if changecount == 0:
            msg = f"No items were {changetype}."
            status = messages.INFO
        else:
            msg = ngettext(
                "Successfully %(changetype)s %(changecount)s %(name)s.",
                "Successfully %(changetype)s %(changecount)s %(name)s.",
                changecount,
            ) % {
                "changetype": changetype,
                "changecount": changecount,
                "name": model_ngettext(self.model._meta, changecount),
            }
            status = messages.SUCCESS
        self.message_user(request, msg, status)

        # Redirect logic - copied from internal method `_response_post_save`
        opts = self.model._meta
        if self.has_view_or_change_permission(request):
            post_url = reverse(
                "admin:%s_%s_changelist" % (opts.app_label, opts.model_name),
                current_app=self.admin_site.name,
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {"preserved_filters": preserved_filters, "opts": opts}, post_url
            )
        else:
            post_url = reverse("admin:index", current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)
