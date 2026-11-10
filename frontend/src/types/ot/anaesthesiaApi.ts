import { HttpMethod, PaginatedResponse, Type } from "@/Utils/request/types";

export type AnaesthesiaStatus = "active" | "inactive";

export interface Anaesthesia {
  id: string;
  anaesthesia_name: string;
  anaesthesia_code: string;
  description: string;
  status: AnaesthesiaStatus;
}

export interface AnaesthesiaWrite {
  anaesthesia_name: string;
  anaesthesia_code: string;
  description: string;
  status: AnaesthesiaStatus;
}

export default {
  list: {
    path: "/api/v1/facility/{facilityId}/anaesthesia/",
    method: HttpMethod.GET,
    TRes: Type<PaginatedResponse<Anaesthesia>>(),
  },
  create: {
    path: "/api/v1/facility/{facilityId}/anaesthesia/",
    method: HttpMethod.POST,
    TRes: Type<Anaesthesia>(),
    TBody: Type<AnaesthesiaWrite>(),
  },
  get: {
    path: "/api/v1/facility/{facilityId}/anaesthesia/{id}/",
    method: HttpMethod.GET,
    TRes: Type<Anaesthesia>(),
  },
  update: {
    path: "/api/v1/facility/{facilityId}/anaesthesia/{id}/",
    method: HttpMethod.PUT,
    TRes: Type<Anaesthesia>(),
    TBody: Type<AnaesthesiaWrite>(),
  },
  delete: {
    path: "/api/v1/facility/{facilityId}/anaesthesia/{id}/",
    method: HttpMethod.DELETE,
    TRes: Type<void>(),
    TBody: Type<void>(),
  },
} as const;
