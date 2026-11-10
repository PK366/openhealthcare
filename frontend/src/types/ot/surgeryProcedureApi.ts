import { HttpMethod, PaginatedResponse, Type } from "@/Utils/request/types";

export type SurgeryProcedureStatus = "active" | "inactive";

export interface SurgeryProcedure {
  id: string;
  procedure_name: string;
  procedure_code: string;
  department: string;
  department_name: string;
  duration_minutes: number;
  description: string;
  status: SurgeryProcedureStatus;
  facility?: { id: string; name: string };
  created_date?: string;
  modified_date?: string;
}

export interface SurgeryProcedureWrite {
  procedure_name: string;
  procedure_code: string;
  department: string;
  duration_minutes: number;
  description: string;
  status: SurgeryProcedureStatus;
}

const surgeryProcedureApi = {
  list: {
    path: "/api/v1/facility/{facilityId}/surgery_procedure/",
    method: HttpMethod.GET,
    TRes: Type<PaginatedResponse<SurgeryProcedure>>(),
  },
  create: {
    path: "/api/v1/facility/{facilityId}/surgery_procedure/",
    method: HttpMethod.POST,
    TRes: Type<SurgeryProcedure>(),
    TBody: Type<SurgeryProcedureWrite>(),
  },
  get: {
    path: "/api/v1/facility/{facilityId}/surgery_procedure/{id}/",
    method: HttpMethod.GET,
    TRes: Type<SurgeryProcedure>(),
  },
  update: {
    path: "/api/v1/facility/{facilityId}/surgery_procedure/{id}/",
    method: HttpMethod.PUT,
    TRes: Type<SurgeryProcedure>(),
    TBody: Type<SurgeryProcedureWrite>(),
  },
  delete: {
    path: "/api/v1/facility/{facilityId}/surgery_procedure/{id}/",
    method: HttpMethod.DELETE,
    TRes: Type<void>(),
    TBody: Type<void>(),
  },
} as const;

export default surgeryProcedureApi;
