import { HttpMethod, PaginatedResponse, Type } from "@/Utils/request/types";

export type OTRoomStatus =
  | "available"
  | "occupied"
  | "maintenance"
  | "inactive";

export interface OTRoom {
  id: string;
  location: string;
  location_name: string;
  description: string;
  equipment_details: string[];
  status: OTRoomStatus;
  surgery_procedures: string[];
  facility?: {
    id: string;
    name: string;
  };
  created_date?: string;
  modified_date?: string;
}

export interface OTRoomWrite {
  location: string;
  description: string;
  equipment_details: string[];
  status: OTRoomStatus;
  surgery_procedures: string[];
}

export default {
  list: {
    path: "/api/v1/facility/{facilityId}/ot_room/",
    method: HttpMethod.GET,
    TRes: Type<PaginatedResponse<OTRoom>>(),
  },

  create: {
    path: "/api/v1/facility/{facilityId}/ot_room/",
    method: HttpMethod.POST,
    TRes: Type<OTRoom>(),
    TBody: Type<OTRoomWrite>(),
  },

  get: {
    path: "/api/v1/facility/{facilityId}/ot_room/{roomId}/",
    method: HttpMethod.GET,
    TRes: Type<OTRoom>(),
  },

  update: {
    path: "/api/v1/facility/{facilityId}/ot_room/{roomId}/",
    method: HttpMethod.PUT,
    TRes: Type<OTRoom>(),
    TBody: Type<OTRoomWrite>(),
  },

  delete: {
    path: "/api/v1/facility/{facilityId}/ot_room/{roomId}/",
    method: HttpMethod.DELETE,
    TRes: Type<Record<string, never>>(),
    TBody: Type<void>(),
  },
} as const;
