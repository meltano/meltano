import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faAngleDown,
  faAngleUp,
  faArrowDown,
  faArrowRight,
  faArrowUp,
  faArrowsAltV,
  faBolt,
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
  faGift,
  faGlobeAmericas,
  faHashtag,
  faInfoCircle,
  faProjectDiagram,
  faSearch,
  faSort,
  faSortAmountDown,
  faSortAmountUp,
  faTable,
  faThLarge,
  faThList,
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
    library.add(faBolt)
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
    library.add(faGift)
    library.add(faGlobeAmericas)
    library.add(faHashtag)
    library.add(faInfoCircle)
    library.add(faProjectDiagram)
    library.add(faSearch)
    library.add(faSort)
    library.add(faSortAmountDown)
    library.add(faSortAmountUp)
    library.add(faTable)
    library.add(faThLarge)
    library.add(faThList)
    library.add(faUser)

    Vue.component('font-awesome-icon', FontAwesomeIcon)
    Vue.component('font-awesome-layers', FontAwesomeLayers)
    Vue.component('font-awesome-layers-text', FontAwesomeLayersText)
  }
}
