export default function ensureObjPropIsReactive(vueSetFn, obj, prop, val = false) {
  if (!obj.prop) {
    vueSetFn(obj, prop, val);
  }
}
