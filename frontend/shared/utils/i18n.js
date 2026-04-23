export function t(dict, key, fallback = "") {
  const value = key.split(".").reduce((acc, part) => {
    if (!acc || typeof acc !== "object") {
      return undefined;
    }
    return acc[part];
  }, dict);

  return typeof value === "string" ? value : fallback || key;
}

export function tx(dict, key, params = {}, fallback = "") {
  const template = t(dict, key, fallback);
  return Object.entries(params).reduce((result, [name, value]) => {
    return result.replaceAll(`{${name}}`, String(value));
  }, template);
}
