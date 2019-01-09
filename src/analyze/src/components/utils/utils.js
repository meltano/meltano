export function ensureObjPropIsReactive(vueSetFn, obj, prop, val = false) {
         if (!obj.hasOwnProperty(prop)) {
           vueSetFn(obj, prop, val);
         }
       }