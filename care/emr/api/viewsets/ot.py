from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from care.emr.api.viewsets.base import EMRModelViewSet
from care.emr.models import OTRoom, SurgeryProcedure, Anaesthesia, SurgeryAnaesthesiaConfig
from care.emr.models.organization import FacilityOrganization
from care.emr.models.location import FacilityLocation
from care.emr.resources.ot.spec import (
    OTRoomWriteSpec,
    OTRoomUpdateSpec,
    OTRoomListSpec,
    OTRoomRetrieveSpec,
    SurgeryProcedureWriteSpec,
    SurgeryProcedureUpdateSpec,
    SurgeryProcedureListSpec,
    SurgeryProcedureRetrieveSpec,
    AnaesthesiaWriteSpec,
    AnaesthesiaUpdateSpec,
    AnaesthesiaListSpec,
    AnaesthesiaRetrieveSpec,
    SurgeryAnaesthesiaConfigWriteSpec,
    SurgeryAnaesthesiaConfigUpdateSpec,
    SurgeryAnaesthesiaConfigListSpec,
    SurgeryAnaesthesiaConfigRetrieveSpec,
)
from care.facility.models import Facility
from care.security.authorization import AuthorizationController
from care.utils.shortcuts import get_object_or_404


class OTRoomViewSet(EMRModelViewSet):
    database_model = OTRoom
    pydantic_model = OTRoomWriteSpec
    pydantic_update_model = OTRoomUpdateSpec
    pydantic_read_model = OTRoomListSpec
    pydantic_retrieve_model = OTRoomRetrieveSpec

    def get_facility_obj(self):
        return get_object_or_404(
            Facility,
            external_id=self.kwargs["facility_external_id"],
        )

    def get_queryset(self):
        facility = self.get_facility_obj()

        return (
            super()
            .get_queryset()
            .filter(
                facility=facility,
                deleted=False,
            )
            .select_related("facility", "location")
            .order_by("location__name")
        )

    def validate_data(self, instance, model_obj=None):
        facility = self.get_facility_obj()

        location = get_object_or_404(
            FacilityLocation,
            external_id=instance.location,
            facility=facility,
            deleted=False,
            mode="instance",
            form="ro",
        )

        if location.status.lower() != "active":
            raise ValidationError(
                {
                    "location": (
                        "Selected room must be active in Location Master."
                    )
                }
            )

        # Validate selected procedures when the field is supplied.
        procedure_ids = instance.surgery_procedures

        if procedure_ids is not None:
            unique_procedure_ids = set(procedure_ids)

            active_procedures = SurgeryProcedure.objects.filter(
                facility=facility,
                external_id__in=unique_procedure_ids,
                deleted=False,
                status="active",
            )

            if active_procedures.count() != len(unique_procedure_ids):
                raise ValidationError(
                    {
                        "surgery_procedures": (
                            "Select only active surgery procedures "
                            "from this facility."
                        )
                    }
                )

        duplicate_qs = OTRoom.objects.filter(
            facility=facility,
            location=location,
            deleted=False,
        )

        if model_obj is not None:
            duplicate_qs = duplicate_qs.exclude(pk=model_obj.pk)

        if duplicate_qs.exists():
            raise ValidationError(
                {
                    "location": (
                        "OT Setup already exists for this room."
                    )
                }
            )

    def authorize_create(self, instance):
        facility = self.get_facility_obj()

        if not AuthorizationController.call(
            "can_create_facility_location_obj",
            self.request.user,
            None,
            facility,
        ):
            raise PermissionDenied(
                "You do not have permission to configure OT rooms."
            )

    def authorize_update(self, request_obj, model_instance):
        if not AuthorizationController.call(
            "can_update_facility_location_obj",
            self.request.user,
            model_instance,
        ):
            raise PermissionDenied(
                "You do not have permission to update OT Setup."
            )

    def authorize_destroy(self, instance):
        self.authorize_update({}, instance)

    def _save_surgery_procedures(self, instance):
        procedure_ids = getattr(
            instance,
            "_surgery_procedure_ids",
            None,
        )

        # None means the request did not supply this field.
        # An empty list clears all assigned procedures.
        if procedure_ids is not None:
            procedures = SurgeryProcedure.objects.filter(
                facility=instance.facility,
                external_id__in=procedure_ids,
                deleted=False,
                status="active",
            )
            instance.surgery_procedures.set(procedures)

    def perform_create(self, instance):
        instance.facility = self.get_facility_obj()

        with transaction.atomic():
            result = super().perform_create(instance)
            self._save_surgery_procedures(instance)

        return result

    def perform_update(self, instance):
        instance.facility = self.get_facility_obj()

        with transaction.atomic():
            result = super().perform_update(instance)
            self._save_surgery_procedures(instance)

        return result

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.updated_by = self.request.user
        instance.save(
            update_fields=[
                "deleted",
                "updated_by",
                "modified_date",
            ]
        )


class SurgeryProcedureViewSet(EMRModelViewSet):
    database_model = SurgeryProcedure
    pydantic_model = SurgeryProcedureWriteSpec
    pydantic_update_model = SurgeryProcedureUpdateSpec
    pydantic_read_model = SurgeryProcedureListSpec
    pydantic_retrieve_model = SurgeryProcedureRetrieveSpec

    def get_facility_obj(self):
        return get_object_or_404(
            Facility,
            external_id=self.kwargs["facility_external_id"],
        )

    def get_queryset(self):
        facility = self.get_facility_obj()

        return (
            super()
            .get_queryset()
            .filter(facility=facility, deleted=False)
            .select_related("facility", "department")
            .order_by("procedure_name")
        )

    def validate_data(self, instance, model_obj=None):
        facility = self.get_facility_obj()

        get_object_or_404(
            FacilityOrganization,
            external_id=instance.department,
            facility=facility,
            # org_type="dept",
            active=True,
        )

        duplicate_qs = SurgeryProcedure.objects.filter(
            facility=facility,
            procedure_code=instance.procedure_code,
            deleted=False,
        )

        if model_obj is not None:
            duplicate_qs = duplicate_qs.exclude(pk=model_obj.pk)

        if duplicate_qs.exists():
            raise ValidationError(
                {
                    "procedure_code": (
                        "This procedure code already exists in this facility."
                    )
                }
            )

    def authorize_create(self, instance):
        facility = self.get_facility_obj()

        if not AuthorizationController.call(
            "can_create_facility_location_obj",
            self.request.user,
            None,
            facility,
        ):
            raise PermissionDenied(
                "You do not have permission to create surgery procedures."
            )

    def authorize_update(self, request_obj, model_instance):
        if not AuthorizationController.call(
            "can_update_facility_location_obj",
            self.request.user,
            model_instance,
        ):
            raise PermissionDenied(
                "You do not have permission to update surgery procedures."
            )

    def authorize_destroy(self, instance):
        self.authorize_update({}, instance)

    def perform_create(self, instance):
        instance.facility = self.get_facility_obj()
        return super().perform_create(instance)

    def perform_update(self, instance):
        instance.facility = self.get_facility_obj()
        return super().perform_update(instance)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.updated_by = self.request.user
        instance.save(
            update_fields=[
                "deleted",
                "updated_by",
                "modified_date",
            ]
        )

class AnaesthesiaViewSet(EMRModelViewSet):
    database_model = Anaesthesia
    pydantic_model = AnaesthesiaWriteSpec
    pydantic_update_model = AnaesthesiaUpdateSpec
    pydantic_read_model = AnaesthesiaListSpec
    pydantic_retrieve_model = AnaesthesiaRetrieveSpec

    def get_facility_obj(self):
        return get_object_or_404(
            Facility,
            external_id=self.kwargs["facility_external_id"],
        )

    def get_queryset(self):
        facility = self.get_facility_obj()

        return (
            super()
            .get_queryset()
            .filter(facility=facility, deleted=False)
            .select_related("facility")
            .order_by("anaesthesia_name")
        )

    def validate_data(self, instance, model_obj=None):
        facility = self.get_facility_obj()

        duplicate_qs = Anaesthesia.objects.filter(
            facility=facility,
            anaesthesia_code=instance.anaesthesia_code,
            deleted=False,
        )

        if model_obj is not None:
            duplicate_qs = duplicate_qs.exclude(pk=model_obj.pk)

        if duplicate_qs.exists():
            raise ValidationError(
                {
                    "anaesthesia_code": (
                        "This anaesthesia code already exists in this facility."
                    )
                }
            )

    def authorize_create(self, instance):
        facility = self.get_facility_obj()

        if not AuthorizationController.call(
            "can_create_facility_location_obj",
            self.request.user,
            None,
            facility,
        ):
            raise PermissionDenied(
                "You do not have permission to create anaesthesia methods."
            )

    def authorize_update(self, request_obj, model_instance):
        if not AuthorizationController.call(
            "can_update_facility_location_obj",
            self.request.user,
            model_instance,
        ):
            raise PermissionDenied(
                "You do not have permission to update anaesthesia methods."
            )

    def authorize_destroy(self, instance):
        self.authorize_update({}, instance)

    def perform_create(self, instance):
        instance.facility = self.get_facility_obj()
        return super().perform_create(instance)

    def perform_update(self, instance):
        instance.facility = self.get_facility_obj()
        return super().perform_update(instance)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.updated_by = self.request.user
        instance.save(
            update_fields=[
                "deleted",
                "updated_by",
                "modified_date",
            ]
        )


class SurgeryAnaesthesiaConfigViewSet(EMRModelViewSet):
    database_model = SurgeryAnaesthesiaConfig
    pydantic_model = SurgeryAnaesthesiaConfigWriteSpec
    pydantic_update_model = SurgeryAnaesthesiaConfigUpdateSpec
    pydantic_read_model = SurgeryAnaesthesiaConfigListSpec
    pydantic_retrieve_model = SurgeryAnaesthesiaConfigRetrieveSpec

    def get_facility_obj(self):
        return get_object_or_404(
            Facility,
            external_id=self.kwargs["facility_external_id"],
        )

    def get_queryset(self):
        facility = self.get_facility_obj()

        return (
            super()
            .get_queryset()
            .filter(
                facility=facility,
                deleted=False,
            )
            .select_related("facility", "surgery_procedure")
            .order_by(
                "surgery_procedure__procedure_name",
                "anaesthesia_format",
            )
        )

    def validate_data(self, instance, model_obj=None):
        facility = self.get_facility_obj()
        procedure_id = getattr(instance, "surgery_procedure", None)

        # surgery_procedure is a UUID in the write spec, not a model instance.
        procedure = SurgeryProcedure.objects.filter(
            external_id=procedure_id,
            facility=facility,
            deleted=False,
            status="active",
        ).first()

        if procedure is None:
            raise ValidationError(
                {
                    "surgery_procedure": (
                        "Select an active surgery procedure "
                        "belonging to this facility."
                    )
                }
            )

    def authorize_create(self, instance):
        facility = self.get_facility_obj()

        if not AuthorizationController.call(
            "can_create_facility_location_obj",
            self.request.user,
            None,
            facility,
        ):
            raise PermissionDenied(
                "You do not have permission to create "
                "surgery anaesthesia configurations."
            )

    def authorize_update(self, request_obj, model_instance):
        if not AuthorizationController.call(
            "can_update_facility_location_obj",
            self.request.user,
            model_instance,
        ):
            raise PermissionDenied(
                "You do not have permission to update "
                "surgery anaesthesia configurations."
            )

    def authorize_destroy(self, instance):
        self.authorize_update({}, instance)

    def perform_create(self, instance):
        instance.facility = self.get_facility_obj()
        return super().perform_create(instance)

    def perform_update(self, instance):
        instance.facility = self.get_facility_obj()
        return super().perform_update(instance)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.updated_by = self.request.user
        instance.save(
            update_fields=[
                "deleted",
                "updated_by",
                "modified_date",
            ]
        )
