import flaskContext from '@/utils/flask'

const FLASK_CONTEXT = flaskContext()

export class UpgradeMiddleware {
  constructor({ toasted }) {
    this.toasted = toasted
    this._killswitch = false
  }

  onResponse(res) {
    if (
      !this._killswitch &&
      FLASK_CONTEXT.version != 'source' &&
      FLASK_CONTEXT.version != res.headers['x-meltano-version']
    ) {
      this._killswitch = true
      this.toasted.global.upgrade()
    }

    return res
  }
}

export default {
  install(Vue, { service, toasted }) {
    service.register(
      new UpgradeMiddleware({
        toasted,
      })
    )
  },
}
