from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import ugettext as _
from rest_framework import serializers

from onadata.apps.main.models.meta_data import MetaData
from onadata.apps.logger.models import XForm

METADATA_TYPES = (
    ('data_license', _(u"Data License")),
    ('form_license', _(u"Form License")),
    ('mapbox_layer', _(u"Mapbox Layer")),
    ('media', _(u"Media")),
    ('public_link', _(u"Public Link")),
    ('source', _(u"Source")),
    ('supporting_doc', _(u"Supporting Document")),
    ('external_export', _(u"External Export")),
)


class MetaDataSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='pk', read_only=True)
    xform = serializers.PrimaryKeyRelatedField(queryset=XForm.objects.all())
    data_value = serializers.CharField(max_length=255,
                                       required=False)
    data_type = serializers.ChoiceField(choices=METADATA_TYPES)
    data_file = serializers.FileField(required=False)
    data_file_type = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = MetaData

    def validate_data_value(self, attrs, source):
        """Ensure we have a valid url if we are adding a media uri
        instead of a media file
        """
        value = attrs.get(source)
        media = attrs.get('data_type')
        data_file = attrs.get('data_file')

        if media == 'media' and data_file is None:
            URLValidator(message=_(u"Invalid url %s." % value))(value)
        if value is None:
            raise ValidationError(u"This field is required.")

        return attrs

    def create(self, validated_data):
        data_type = validated_data.get('data_type')
        data_file = validated_data.get('data_file')
        xform = validated_data.get('xform')
        data_value = data_file.name if data_file else validated_data.get('data_value')
        data_file_type = data_file.content_type if data_file else None

        return MetaData(
            data_type=data_type,
            xform=xform,
            data_value=data_value,
            data_file=data_file,
            data_file_type=data_file_type
        )

