"""Django models for nautobot_plugin_device_lifecycle_mgmt plugin."""

from datetime import datetime

from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from nautobot.extras.models.change_logging import ChangeLoggedModel
from nautobot.core.models import BaseModel


class HardwareLCM(BaseModel, ChangeLoggedModel):
    """HardwareLCMNotice model for plugin."""

    # Set model columns
    device_type = models.ForeignKey(to="dcim.DeviceType", on_delete=models.CASCADE, verbose_name="Device Type")
    release_date = models.DateField(null=True, blank=True, verbose_name="Release Date")
    end_of_sale = models.DateField(null=True, blank=True, verbose_name="End of Sale")
    end_of_support = models.DateField(null=True, blank=True, verbose_name="End of Support")
    end_of_sw_releases = models.DateField(null=True, blank=True, verbose_name="End of Software Releases")
    end_of_security_patches = models.DateField(null=True, blank=True, verbose_name="End of Security Patches")
    documentation_url = models.URLField(blank=True, verbose_name="Documentation URL")
    comments = models.TextField(blank=True)

    csv_headers = [
        "device_type",
        "release_date",
        "end_of_sale",
        "end_of_support",
        "end_of_sw_releases",
        "end_of_security_patches",
        "documentation_url",
        "comments",
    ]

    class Meta:
        """Meta attributes for HardwareLCM."""

        ordering = ("end_of_support", "end_of_sale")
        constraints = [models.UniqueConstraint(fields=["device_type"], name="unique_device_type")]

    def __str__(self):
        """String representation of HardwareLCMs."""
        if self.end_of_support:
            msg = f"{self.device_type} - End of support: {self.end_of_support}"
        else:
            msg = f"{self.device_type} - End of sale: {self.end_of_sale}"
        return msg

    def get_absolute_url(self):
        """Returns the Detail view for HardwareLCM models."""
        return reverse("plugins:nautobot_plugin_device_lifecycle_mgmt:hardwarelcm", kwargs={"pk": self.pk})

    @property
    def expired(self):
        """Return True or False if chosen field is expired."""
        expired_field = settings.PLUGINS_CONFIG["nautobot_plugin_device_lifecycle_mgmt"].get(
            "expired_field", "end_of_support"
        )

        # If the chosen or default field does not exist, default to one of the required fields that are present
        if not getattr(self, expired_field) and not getattr(self, "end_of_support"):
            expired_field = "end_of_sale"
        elif not getattr(self, expired_field) and not getattr(self, "end_of_sale"):
            expired_field = "end_of_support"

        today = datetime.today().date()
        return today >= getattr(self, expired_field)

    def clean(self):
        """Override clean to do custom validation."""
        super().clean()

        if not self.end_of_sale and not self.end_of_support:
            raise ValidationError(_("End of Sale or End of Support must be specified."))

    def to_csv(self):
        """Return fields for bulk view."""
        return (
            self.device_type,
            self.release_date,
            self.end_of_sale,
            self.end_of_support,
            self.end_of_sw_releases,
            self.end_of_security_patches,
            self.documentation_url,
        )
