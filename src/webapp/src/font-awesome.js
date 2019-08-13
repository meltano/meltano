import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faAngleDown,
  faAngleUp,
  faArrowDown,
  faArrowsAltV,
  faArrowRight,
  faArrowUp,
  faCaretDown,
  faCaretUp,
  faCertificate,
  faChartArea,
  faChartBar,
  faChartLine,
  faChartPie,
  faCheck,
  faDotCircle,
  faDraftingCompass,
  faExclamationTriangle,
  faFilter,
  faGlobeAmericas,
  faHashtag,
  faInfoCircle,
  faTable,
  faSearch,
  faSort,
  faSortAmountDown,
  faSortAmountUp,
  faUser
} from '@fortawesome/free-solid-svg-icons'
import {
  FontAwesomeIcon,
  FontAwesomeLayers,
  FontAwesomeLayersText
} from '@fortawesome/vue-fontawesome'

export default {
  install(Vue) {
    library.add(faAngleDown)
    library.add(faAngleUp)
    library.add(faArrowsAltV)
    library.add(faArrowDown)
    library.add(faArrowRight)
    library.add(faArrowUp)
    library.add(faCaretDown)
    library.add(faCaretUp)
    library.add(faCertificate)
    library.add(faChartArea)
    library.add(faChartBar)
    library.add(faChartLine)
    library.add(faChartPie)
    library.add(faCheck)
    library.add(faDotCircle)
    library.add(faDraftingCompass)
    library.add(faExclamationTriangle)
    library.add(faFilter)
    library.add(faGlobeAmericas)
    library.add(faHashtag)
    library.add(faInfoCircle)
    library.add(faTable)
    library.add(faSearch)
    library.add(faSort)
    library.add(faSortAmountDown)
    library.add(faSortAmountUp)
    library.add(faUser)

    Vue.component('font-awesome-icon', FontAwesomeIcon)
    Vue.component('font-awesome-layers', FontAwesomeLayers)
    Vue.component('font-awesome-layers-text', FontAwesomeLayersText)
  }
}
