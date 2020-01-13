import lodash from 'lodash'

import flaskContext from '@/flask'
import moment from 'moment'
import { namer } from '@/utils/mappers'

const regExpConnectorLogo = /(?:tap-|target-)?(.*)/
const regExpPrivateInput = /(password|private|secret|token)/

const FLASK = flaskContext()

export default {
  // Path Utils
  root(path = '/') {
    // window.FLASK should be injected in the template
    // either by Webpack (dev) or Flask (prod)

    if (FLASK.appUrl) {
      return `${FLASK.appUrl}${path}`
    } else {
      return path
    }
  },

  apiRoot(path = '/') {
    return this.root(`/api/v1${path}`)
  },

  apiUrl(blueprint, location = '') {
    const path = [blueprint, location].join('/')
    return this.apiRoot().concat(path)
  },

  docsUrl(path = '/', fragment) {
    fragment = fragment ? `#${fragment}` : ''

    return `https://meltano.com/docs${path}.html${fragment}`
  },

  downloadBlobAsFile(blob, fileName) {
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  },

  getConnectorLogoUrl(connectorName) {
    connectorName = connectorName === 'postgresql' ? 'postgres' : connectorName
    const name = regExpConnectorLogo.exec(connectorName)[1]

    return `/static/logos/${name}-logo.png`
  },

  getIsSubRouteOf(parentPath, currentPath) {
    return currentPath.indexOf(parentPath) === 0
  },

  scrollToBottom(element = window) {
    this.scrollToTarget(element, Number.MAX_SAFE_INTEGER)
  },

  scrollToTarget(element, top) {
    element.scrollTo({ top, left: 0, behavior: 'smooth' })
  },

  scrollToTop(element = window) {
    this.scrollToTarget(element, 0)
  },

  // Color Utils
  colors: {
    backgroundColor: [
      'rgba(255, 99, 132, 0.2)',
      'rgba(54, 162, 235, 0.2)',
      'rgba(255, 206, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(153, 102, 255, 0.2)',
      'rgba(255, 159, 64, 0.2)'
    ],
    borderColor: [
      'rgba(255,99,132,1)',
      'rgba(54, 162, 235, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)',
      'rgba(255, 159, 64, 1)'
    ]
  },

  getColor(i) {
    // assume they are the same length;
    const colorLength = this.colors.backgroundColor.length
    return {
      backgroundColor: this.colors.backgroundColor[i % colorLength],
      borderColor: this.colors.borderColor[i % colorLength]
    }
  },

  // Collection Utils
  difference(arr1, arr2) {
    return arr1
      .filter(x => !arr2.includes(x))
      .concat(arr2.filter(x => !arr1.includes(x)))
  },

  deepFreeze(object) {
    // Inspired by https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze
    const propNames = Object.getOwnPropertyNames(object)
    // eslint-disable-next-line no-restricted-syntax
    for (const name of propNames) {
      const value = object[name]
      // eslint-disable-next-line no-undef
      object[name] =
        value && typeof value === 'object' ? this.deepFreeze(value) : value
    }
    return Object.freeze(object)
  },

  // String Utils
  capitalize(value) {
    if (!value) {
      return ''
    }
    const capMe = value.toString()
    return capMe.charAt(0).toUpperCase() + capMe.slice(1)
  },
  extractFileNameFromPath(path) {
    return path.replace(/^.*[\\/]/, '')
  },
  hyphenate(value, prepend) {
    if (!value) {
      return ''
    }
    let hyphenateMe = `${prepend}-` || ''
    hyphenateMe += value.toLowerCase().replace(/\s\s*/g, '-')
    return hyphenateMe
  },
  inferInputType(value) {
    return regExpPrivateInput.test(value) ? 'password' : 'text'
  },
  jsDashify(type, name) {
    if (!type || !name) {
      return ''
    }
    return this.hyphenate(name, `js-${type.toLowerCase()}`)
  },
  pretty(value) {
    try {
      return JSON.stringify(JSON.parse(value), null, 2)
    } catch (e) {
      return value
    }
  },
  requiredConnectorSettingsKeys(settings, groupValidation) {
    return groupValidation
      ? lodash.intersection(...groupValidation)
      : settings.map(namer)
  },
  singularize(value) {
    if (!value) {
      return ''
    }
    // A more robust implementation is encouraged (currently assumes English and 's' at tail)
    let singularizeMe = value.toString()
    const lastChar = singularizeMe[singularizeMe.length - 1]
    if (lastChar.toLowerCase() === 's') {
      singularizeMe = singularizeMe.slice(0, -1)
    }
    return singularizeMe
  },
  snowflakeAccountParser(account) {
    const domainFlag = 'snowflakecomputing.com'
    const domainLocation = account.indexOf(domainFlag)
    let accountId = ''

    // If the domain exists in user input, assume URL
    if (domainLocation > -1) {
      let shortenedUrl = account.slice(0, domainLocation + domainFlag.length)

      // Clean up URL if http is detected
      if (shortenedUrl.indexOf('http') > -1) {
        shortenedUrl = shortenedUrl.slice(shortenedUrl.indexOf('//') + 2)
      }

      // This could eventually parse data like region if needed
      accountId = shortenedUrl.split('.')[0]
    }

    return accountId
  },
  titleCase(value) {
    return value.replace(
      /\w\S*/g,
      txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    )
  },
  truncate(string, max = 50) {
    if (string.length > max) {
      return `${string.substring(0, max)}...`
    }
    return string
  },
  underscoreToSpace(value) {
    return value.replace(/_/g, ' ')
  },

  // Date Utils
  dateIso8601(dateString) {
    return `${new Date(dateString).toISOString().split('.')[0]}Z`
  },

  dateIso8601Nullable(dateString) {
    return dateString ? this.dateIso8601(dateString) : null
  },

  getFirstOfMonthAsIso8601() {
    const date = new Date()
    const firstOfThisMonth = new Date(
      date.getFullYear(),
      date.getMonth(),
      1
    ).toString()
    return this.dateIso8601(firstOfThisMonth)
  },

  getInputDateMeta() {
    return {
      min: '2000-01-01',
      pattern: '[0-9]{4}-[0-9]{2}-[0-9]{2}',
      today: this.formatDateStringYYYYMMDD(new Date())
    }
  },

  getIsDateStringInFormatYYYYMMDD(dateString) {
    const result = /[0-9]{4}-[0-9]{2}-[0-9]{2}/.test(dateString)
    return result
  },

  formatDateStringYYYYMMDD(date) {
    return new Date(date).toISOString().split('T')[0]
  },

  // Time Utils
  momentFromNow(val) {
    return moment(val).fromNow()
  },

  momentFormatlll(val) {
    return moment(val).format('lll')
  },

  momentHumanizedDuration(startDate, endDate) {
    const x = new moment(startDate)
    const y = new moment(endDate)
    const duration = moment.duration(y.diff(x))
    const formatter = (val, append) => (val ? `${val} ${append} ` : '')
    const strDays = formatter(duration.days(), 'days')
    const strHour = formatter(duration.hours(), 'hours')
    const strMin = formatter(duration.minutes(), 'min')
    const strSec = formatter(duration.seconds(), 'sec')
    return `${strDays}${strHour}${strMin}${strSec}`
  }
}
