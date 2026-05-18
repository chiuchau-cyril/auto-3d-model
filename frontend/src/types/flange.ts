export type FlangeSpec = {
  inner_diameter_mm: number;
  pcd_mm: number;
  outer_diameter_mm: number;
  bolt_hole_count: number;
  bolt_hole_diameter_mm: number;
  thickness_mm: number;
  material: "SS400";
};

export type ApiErrorItem = {
  field: string;
  message: string;
};

export type ApiErrorResponse = {
  errors: ApiErrorItem[];
};

export type HealthResponse = {
  status: "ok";
  oda_converter_available: boolean;
  version?: string;
};
