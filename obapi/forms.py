from django import forms

from obapi.models import OBContentItem, SpotifyContentItem, YoutubeContentItem


class AddContentItemForm(forms.ModelForm):
    class Meta:
        fields = ("item_id",)

    def save(self):
        item_id = self.cleaned_data.pop("item_id")
        return self.Meta.model.objects.create_item(item_id)


class AddYoutubeContentItemForm(AddContentItemForm):
    class Meta(AddContentItemForm.Meta):
        model = YoutubeContentItem


class AddSpotifyContentItemForm(AddContentItemForm):
    class Meta(AddContentItemForm.Meta):
        model = SpotifyContentItem


class AddOBContentItemForm(AddContentItemForm):
    class Meta(AddContentItemForm.Meta):
        model = OBContentItem
