import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { FlangeForm } from "@/components/FlangeForm";

const FIELD_IDS = [
  "field-inner_diameter_mm",
  "field-pcd_mm",
  "field-outer_diameter_mm",
  "field-bolt_hole_count",
  "field-bolt_hole_diameter_mm",
  "field-thickness_mm",
  "field-material",
];

function fillField(testId: string, value: string) {
  const input = screen.getByTestId(testId);
  fireEvent.change(input, { target: { value } });
}

function fillAllValid() {
  fillField("field-inner_diameter_mm", "100");
  fillField("field-pcd_mm", "150");
  fillField("field-outer_diameter_mm", "200");
  fillField("field-bolt_hole_count", "4");
  fillField("field-bolt_hole_diameter_mm", "10");
  fillField("field-thickness_mm", "12");
}

describe("FlangeForm", () => {
  it("renders all 7 field inputs", () => {
    render(<FlangeForm onSubmit={vi.fn()} />);
    for (const id of FIELD_IDS) {
      expect(screen.getByTestId(id)).toBeInTheDocument();
    }
  });

  it("material field is disabled and shows SS400", () => {
    render(<FlangeForm onSubmit={vi.fn()} />);
    const material = screen.getByTestId("field-material");
    expect(material).toBeDisabled();
    expect(material).toHaveValue("SS400");
  });

  it("submit button is disabled when form is empty", () => {
    render(<FlangeForm onSubmit={vi.fn()} />);
    expect(screen.getByTestId("submit")).toBeDisabled();
  });

  it("submit button is disabled when input is invalid (PCD <= inner diameter)", () => {
    render(<FlangeForm onSubmit={vi.fn()} />);
    fillField("field-inner_diameter_mm", "150");
    fillField("field-pcd_mm", "100");
    fillField("field-outer_diameter_mm", "200");
    fillField("field-bolt_hole_count", "4");
    fillField("field-bolt_hole_diameter_mm", "10");
    fillField("field-thickness_mm", "12");
    expect(screen.getByTestId("submit")).toBeDisabled();
  });

  it("submit button is enabled after filling all valid values", () => {
    render(<FlangeForm onSubmit={vi.fn()} />);
    fillAllValid();
    expect(screen.getByTestId("submit")).not.toBeDisabled();
  });

  it("calls onSubmit with parsed spec when submit is clicked", () => {
    const onSubmit = vi.fn();
    render(<FlangeForm onSubmit={onSubmit} />);
    fillAllValid();
    fireEvent.click(screen.getByTestId("submit"));
    expect(onSubmit).toHaveBeenCalledOnce();
    expect(onSubmit).toHaveBeenCalledWith({
      inner_diameter_mm: 100,
      pcd_mm: 150,
      outer_diameter_mm: 200,
      bolt_hole_count: 4,
      bolt_hole_diameter_mm: 10,
      thickness_mm: 12,
      material: "SS400",
    });
  });

  it("shows PCD error when PCD <= inner diameter", () => {
    render(<FlangeForm onSubmit={vi.fn()} />);
    fillField("field-inner_diameter_mm", "150");
    fillField("field-pcd_mm", "100");
    fillField("field-outer_diameter_mm", "200");
    fillField("field-bolt_hole_count", "4");
    fillField("field-bolt_hole_diameter_mm", "10");
    fillField("field-thickness_mm", "12");
    const errSpan = screen.getByTestId("error-pcd_mm");
    expect(errSpan).toBeInTheDocument();
    expect(errSpan).toHaveTextContent("PCD 必須大於內徑");
  });

  it("shows outer diameter error when outer <= PCD", () => {
    render(<FlangeForm onSubmit={vi.fn()} />);
    fillField("field-inner_diameter_mm", "100");
    fillField("field-pcd_mm", "150");
    fillField("field-outer_diameter_mm", "150");
    fillField("field-bolt_hole_count", "4");
    fillField("field-bolt_hole_diameter_mm", "10");
    fillField("field-thickness_mm", "12");
    const errSpan = screen.getByTestId("error-outer_diameter_mm");
    expect(errSpan).toBeInTheDocument();
    expect(errSpan).toHaveTextContent("外徑必須大於 PCD");
  });

  it("submit button is disabled when busy prop is true even with valid values", () => {
    render(<FlangeForm onSubmit={vi.fn()} busy={true} />);
    fillAllValid();
    expect(screen.getByTestId("submit")).toBeDisabled();
  });
});
