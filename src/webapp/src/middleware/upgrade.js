import axios from 'axios'
import { Service } from 'axios-middleware'
import flaskContext from '@/flask'


const FLASK_CONTEXT = flaskContext()


export class UpgradeMiddleware {
  constructor({ toasted }) {
    this.toasted = toasted
    this._disabled = false
  }

  onResponse(res) {
    console.info(res.headers)

    if (!this._disabled
      && FLASK_CONTEXT.version != "source"
      && FLASK_CONTEXT.version != res.headers["x-meltano-version"]) {
      this._disabled = true
      this.toasted.global.upgrade()
    }

    return res
  }
}

export default {
  install(Vue, options) {
    const service = new Service(axios)

    service.register(
      new UpgradeMiddleware({
        toasted: options.toasted
      })
    )
  }
}
