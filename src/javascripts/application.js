/* global fetch, turf */
import SelectOrNew from './modules/select-or-new'
import MultiSelect from './modules/multi-select'
import MultiSelectOrNew from './modules/multi-select-or-new'
import * as cookies from './modules/cookies'

window.dptp = {
  SelectOrNew: SelectOrNew,
  MultiSelect: MultiSelect,
  MultiSelectOrNew: MultiSelectOrNew,
  cookies: cookies
}

// Initialize cookie banner when the module loads
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function() {
    cookies.showCookieBannerIfNotSetAndSetTrackingCookies();
  });
}
