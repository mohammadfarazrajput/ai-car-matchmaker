export const A2UI_VERSION = "1.0" as const;

export type DynamicValue =
  string | number | boolean | { path: string } | { call: string; args: Record<string, unknown> };

export interface Action {
  event: { name: string; context?: Record<string, unknown> };
}

export interface ComponentBase {
  id: string;
  component: string;
  weight?: number;
}

export interface TextComponent extends ComponentBase {
  component: "Text";
  text: DynamicValue;
  variant?: "caption" | "body";
}

export interface ImageComponent extends ComponentBase {
  component: "Image";
  url: DynamicValue;
  description?: DynamicValue;
  fit?: "contain" | "cover" | "fill" | "none" | "scaleDown";
  variant?: "icon" | "avatar" | "smallFeature" | "mediumFeature" | "largeFeature" | "header";
}

export interface IconComponent extends ComponentBase {
  component: "Icon";
  name: string | { svgPath: DynamicValue } | { path: string };
}

export interface RowComponent extends ComponentBase {
  component: "Row";
  children: string[] | { path: string; componentId: string };
  justify?: "center" | "end" | "spaceAround" | "spaceBetween" | "spaceEvenly" | "start" | "stretch";
  align?: "start" | "center" | "end" | "stretch";
}

export interface ColumnComponent extends ComponentBase {
  component: "Column";
  children: string[] | { path: string; componentId: string };
  justify?: "start" | "center" | "end" | "spaceBetween" | "spaceAround" | "spaceEvenly" | "stretch";
  align?: "center" | "end" | "start" | "stretch";
}

export interface ListComponent extends ComponentBase {
  component: "List";
  children: string[] | { path: string; componentId: string };
  direction?: "vertical" | "horizontal";
  align?: "start" | "center" | "end" | "stretch";
}

export interface CardComponent extends ComponentBase {
  component: "Card";
  child?: string;
  title?: DynamicValue;
  subtitle?: DynamicValue;
  imageUrl?: DynamicValue;
  body?: DynamicValue;
  action?: Action;
}

export interface ButtonComponent extends ComponentBase {
  component: "Button";
  child?: string;
  label?: DynamicValue;
  variant?: "default" | "primary" | "borderless";
  action?: Action;
}

export interface TextFieldComponent extends ComponentBase {
  component: "TextField";
  label: DynamicValue;
  value?: DynamicValue;
  placeholder?: DynamicValue;
  variant?: "longText" | "number" | "shortText" | "obscured";
  action?: Action;
}

export interface ChoicePickerComponent extends ComponentBase {
  component: "ChoicePicker";
  label?: DynamicValue;
  options: Array<{ label: DynamicValue; value: string }>;
  value: DynamicValue;
  variant?: "multipleSelection" | "mutuallyExclusive";
  displayStyle?: "checkbox" | "chips";
  action?: Action;
}

export interface SliderComponent extends ComponentBase {
  component: "Slider";
  label?: DynamicValue;
  min?: number;
  max: number;
  value: DynamicValue;
  steps?: number;
  action?: Action;
}

export interface DateTimeInputComponent extends ComponentBase {
  component: "DateTimeInput";
  value: DynamicValue;
  enableDate?: boolean;
  enableTime?: boolean;
  label?: DynamicValue;
  min?: DynamicValue;
  max?: DynamicValue;
  action?: Action;
}

export interface DividerComponent extends ComponentBase {
  component: "Divider";
  axis?: "horizontal" | "vertical";
}

export type A2UIComponent =
  | TextComponent
  | ImageComponent
  | IconComponent
  | RowComponent
  | ColumnComponent
  | ListComponent
  | CardComponent
  | ButtonComponent
  | TextFieldComponent
  | ChoicePickerComponent
  | SliderComponent
  | DateTimeInputComponent
  | DividerComponent
  | (ComponentBase & Record<string, unknown>);

export interface CreateSurface {
  surfaceId: string;
  components: A2UIComponent[];
  dataModel?: Record<string, unknown>;
}

export interface UpdateComponents {
  surfaceId: string;
  components: A2UIComponent[];
}

export interface UpdateDataModel {
  surfaceId: string;
  path: string;
  value: unknown;
}

export interface DeleteSurface {
  surfaceId: string;
}

export interface A2UIFrame {
  version: string;
  createSurface?: CreateSurface;
  updateComponents?: UpdateComponents;
  updateDataModel?: UpdateDataModel;
  deleteSurface?: DeleteSurface;
}
