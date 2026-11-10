from enum import Enum

from pydantic import UUID4, Field

from care.emr.models.location import FacilityLocation
from care.emr.models.ot import OTRoom, SurgeryProcedure, Anaesthesia
from care.emr.resources.base import EMRResource


class OTRoomStatusChoices(str, Enum):
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"
    inactive = "inactive"


class OTRoomBaseSpec(EMRResource):
    __model__ = OTRoom
    __exclude__ = ["facility"]

    id: UUID4 | None = None


class OTRoomSpec(OTRoomBaseSpec):
    location: UUID4
    description: str = ""
    equipment_details: list = Field(default_factory=list)
    status: OTRoomStatusChoices = OTRoomStatusChoices.available

    def perform_extra_deserialization(self, is_update, obj):
        location = FacilityLocation.objects.get(
            external_id=self.location,
            deleted=False,
        )
        obj.location = location


class OTRoomWriteSpec(OTRoomSpec):
    pass


class OTRoomUpdateSpec(OTRoomSpec):
    pass


class OTRoomListSpec(OTRoomSpec):
    facility: dict | None = None
    location_name: str | None = None
    created_date: str | None = None
    modified_date: str | None = None

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        mapping["id"] = obj.external_id
        mapping["location"] = str(obj.location.external_id)
        mapping["location_name"] = obj.location.name
        mapping["facility"] = {
            "id": str(obj.facility.external_id),
            "name": obj.facility.name,
        }
        mapping["created_date"] = (
            obj.created_date.isoformat() if obj.created_date else None
        )
        mapping["modified_date"] = (
            obj.modified_date.isoformat() if obj.modified_date else None
        )


class OTRoomRetrieveSpec(OTRoomListSpec):
    created_by: dict | None = None
    updated_by: dict | None = None

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        super().perform_extra_serialization(mapping, obj)
        cls.serialize_audit_users(mapping, obj)


class SurgeryProcedureStatusChoices(str, Enum):
    active = "active"
    inactive = "inactive"


class SurgeryProcedureBaseSpec(EMRResource):
    __model__ = SurgeryProcedure
    __exclude__ = ["facility"]

    id: UUID4 | None = None


class SurgeryProcedureSpec(SurgeryProcedureBaseSpec):
    procedure_name: str = Field(min_length=1, max_length=255)
    procedure_code: str = Field(min_length=1, max_length=100)
    department: UUID4
    duration_minutes: int = Field(default=30, ge=1)
    description: str = ""
    status: SurgeryProcedureStatusChoices = SurgeryProcedureStatusChoices.active

    def perform_extra_deserialization(self, is_update, obj):
        from care.emr.models.organization import FacilityOrganization

        obj.department = FacilityOrganization.objects.get(
            external_id=self.department
        )
        
class SurgeryProcedureWriteSpec(SurgeryProcedureSpec):
    pass


class SurgeryProcedureUpdateSpec(SurgeryProcedureSpec):
    pass


class SurgeryProcedureListSpec(SurgeryProcedureSpec):
    facility: dict | None = None
    department_name: str | None = None
    created_date: str | None = None
    modified_date: str | None = None

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        mapping["id"] = str(obj.external_id)
        mapping["department"] = str(obj.department.external_id)
        mapping["department_name"] = obj.department.name
        mapping["facility"] = {
            "id": str(obj.facility.external_id),
            "name": obj.facility.name,
        }
        mapping["created_date"] = (
            obj.created_date.isoformat() if obj.created_date else None
        )
        mapping["modified_date"] = (
            obj.modified_date.isoformat() if obj.modified_date else None
        )


class SurgeryProcedureRetrieveSpec(SurgeryProcedureListSpec):
    created_by: dict | None = None
    updated_by: dict | None = None

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        super().perform_extra_serialization(mapping, obj)
        cls.serialize_audit_users(mapping, obj)

class AnaesthesiaStatusChoices(str, Enum):
    active = "active"
    inactive = "inactive"


class AnaesthesiaBaseSpec(EMRResource):
    __model__ = Anaesthesia
    __exclude__ = ["facility"]

    id: UUID4 | None = None


class AnaesthesiaSpec(AnaesthesiaBaseSpec):
    anaesthesia_name: str = Field(min_length=1, max_length=255)
    anaesthesia_code: str = Field(min_length=1, max_length=100)
    description: str = ""
    status: AnaesthesiaStatusChoices = AnaesthesiaStatusChoices.active


class AnaesthesiaWriteSpec(AnaesthesiaSpec):
    pass


class AnaesthesiaUpdateSpec(AnaesthesiaSpec):
    pass


class AnaesthesiaListSpec(AnaesthesiaSpec):
    facility: dict | None = None
    created_date: str | None = None
    modified_date: str | None = None

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        mapping["id"] = str(obj.external_id)
        mapping["facility"] = {
            "id": str(obj.facility.external_id),
            "name": obj.facility.name,
        }
        mapping["created_date"] = (
            obj.created_date.isoformat() if obj.created_date else None
        )
        mapping["modified_date"] = (
            obj.modified_date.isoformat() if obj.modified_date else None
        )


class AnaesthesiaRetrieveSpec(AnaesthesiaListSpec):
    created_by: dict | None = None
    updated_by: dict | None = None

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        super().perform_extra_serialization(mapping, obj)
        cls.serialize_audit_users(mapping, obj)
