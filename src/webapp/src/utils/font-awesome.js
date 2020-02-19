import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faAngleDown,
  faAngleUp,
  faArrowDown,
  faArrowRight,
  faArrowUp,
  faArrowsAltV,
  faBell,
  faBolt,
  faBookOpen,
  faCaretDown,
  faCaretUp,
  faCertificate,
  faChartArea,
  faChartBar,
  faChartLine,
  faChartPie,
  faCheck,
  faCheckCircle,
  faDatabase,
  faDotCircle,
  faDraftingCompass,
  faEnvelope,
  faExclamationTriangle,
  faExternalLinkSquareAlt,
  faFileAlt,
  faFileUpload,
  faFileDownload,
  faFilter,
  faGift,
  faGlobeAmericas,
  faHashtag,
  faInfoCircle,
  faLock,
  faPlus,
  faProjectDiagram,
  faQuestionCircle,
  faSync,
  faSearch,
  faSort,
  faSortAmountDown,
  faSortAmountUp,
  faStream,
  faTable,
  faThLarge,
  faThList,
  faTrashAlt,
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
    library.add(faBell)
    library.add(faBolt)
    library.add(faBookOpen)
    library.add(faCaretDown)
    library.add(faCaretUp)
    library.add(faCertificate)
    library.add(faChartArea)
    library.add(faChartBar)
    library.add(faChartLine)
    library.add(faChartPie)
    library.add(faCheck)
    library.add(faCheckCircle)
    library.add(faDatabase)
    library.add(faDotCircle)
    library.add(faDraftingCompass)
    library.add(faEnvelope)
    library.add(faExclamationTriangle)
    library.add(faExternalLinkSquareAlt)
    library.add(faFileAlt)
    library.add(faFileUpload)
    library.add(faFileDownload)
    library.add(faFilter)
    library.add(faGift)
    library.add(faGlobeAmericas)
    library.add(faHashtag)
    library.add(faInfoCircle)
    library.add(faLock)
    library.add(faPlus)
    library.add(faProjectDiagram)
    library.add(faQuestionCircle)
    library.add(faSync)
    library.add(faSearch)
    library.add(faSort)
    library.add(faSortAmountDown)
    library.add(faSortAmountUp)
    library.add(faStream)
    library.add(faTable)
    library.add(faThLarge)
    library.add(faThList)
    library.add(faTrashAlt)
    library.add(faUser)

    Vue.component('font-awesome-icon', FontAwesomeIcon)
    Vue.component('font-awesome-layers', FontAwesomeLayers)
    Vue.component('font-awesome-layers-text', FontAwesomeLayersText)
  }
}
