export default class Filter {
  constructor({
    type = "samplemeta",
    key = "",
    comparison = "eq",
    value = [],
  } = {}) {
    this.type = type;
    this.key = key;
    this.cmp = comparison;
    this.value = value;
  }
}

export const DATE_FORMAT = "yyyy-MM-dd";
