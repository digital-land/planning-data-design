(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
  typeof define === 'function' && define.amd ? define(['exports'], factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.DLFrontend = {}));
})(this, (function (exports) { 'use strict';

  function convertNodeListToArray$1 (nl) {
    return Array.prototype.slice.call(nl)
  }

  // Back to top module as seen in govuk-design-system
  // https://github.com/alphagov/govuk-design-system/blob/master/src/javascripts/components/back-to-top.js
  function BackToTop($module) {
    this.$module = $module;
  }

  BackToTop.prototype.init = function (params) {
    this.setupOptions(params);
    // Check if we can use Intersection Observers
    if (!("IntersectionObserver" in window)) {
      // If there's no support fallback to regular behaviour
      // Since JavaScript is enabled we can remove the default hidden state
      return this.$module.classList.remove(this.hideClass);
    }

    var $start = document.querySelector(this.startElementSelector);
    var $end = document.querySelector(this.endElementSelector);

    // Check if there is anything to observe
    if (!$end || !$start) {
      return;
    }

    let endIsIntersecting = false;
    let startIsIntersecting = false;
    let startIntersectionRatio = 0;

    var observer = new window.IntersectionObserver(
      function (entries) {
        // Find the elements we care about from the entries
        var endEntry = entries.find(function (entry) {
          return entry.target === $end;
        });
        var startEntry = entries.find(function (entry) {
          return entry.target === $start;
        });

        // If there is an entry this means the element has changed so lets check if it's intersecting.
        if (endEntry) {
          endIsIntersecting = endEntry.isIntersecting;
        }
        if (startEntry) {
          startIsIntersecting = startEntry.isIntersecting;
          startIntersectionRatio = startEntry.intersectionRatio;
        }

        // If the subnav or the footer not visible then fix the back to top link to follow the user
        if (startIsIntersecting || endIsIntersecting) {
          this.$module.classList.remove(this.fixClass);
        } else {
          this.$module.classList.add(this.fixClass);
        }

        // If the subnav is visible but you can see it all at once, then a back to top link is likely not as useful.
        // We hide the link but make it focusable for screen readers users who might still find it useful.
        if (startIsIntersecting && startIntersectionRatio === 1) {
          this.$module.classList.add(this.hideClass);
        } else {
          this.$module.classList.remove(this.hideClass);
        }
      }.bind(this)
    );

    observer.observe($end);
    observer.observe($start);
  };

  BackToTop.prototype.passedBottom = function ($el) {
    var $elPos = $el.getClientRects();
    var viewportBottom = window.scrollY + window.innerHeight;
    return $elPos < viewportBottom;
  };

  BackToTop.prototype.setupOptions = function (params) {
    params = params || {};
    this.endElementSelector = params.endElementSelector || ".back-to-top__end";
    this.startElementSelector = params.startElementSelector || ".back-to-top__start";
    this.hideClass = params.hideClass || "back-to-top--hidden";
    this.fixClass = params.fixClass || "back-to-top--fixed";
  };

  // ====================================
  // Filter checkboxes module
  // ====================================

  // to do (see https://www.gov.uk/search/all?keywords=publications&content_purpose_supergroup%5B%5D=services&organisations%5B%5D=academy-for-social-justice&order=relevance)
  // - aria-describedby, hidden span that counts how many options are showing and how many of them are selected
  // - aria-controls, indicate that it controls the list of checkboxes
  // - hide textbox when no js

  function FilterCheckboxes ($module) {
    this.$module = $module;
    this.$textbox = $module.querySelector('.dl-filter-group__auto-filter__input');
  }

  FilterCheckboxes.prototype.init = function (params) {
    this.setupOptions(params);
    var $module = this.$module;
    this.checkboxArr = [...$module.querySelectorAll(this.listItemSelector)];
    var $checkboxes = this.checkboxArr;

    // if no checkboxes then return
    if (!$checkboxes) {
      return
    }

    // returns true is the item has been hidden with display:none
    this.isDisplayNone = function (el) {
      var style = window.getComputedStyle(el);
      return ((style.display === 'none') || (style.visibility === 'hidden'))
    };

    // returns true if the item's checkbox is checked
    this.isItemChecked = function (el) {
      var chbx = el.querySelector('input');
      return chbx.checked
    };

    this.ariaDescription = $module.querySelector('.dl-filter-group__auto-filter__desc');
    // To do: check it exists
    // set initial aria message
    var boundUpdateAriaDescribedBy = this.updateAriaDescribedBy.bind(this);
    boundUpdateAriaDescribedBy();

    // Bind event changes to the textarea
    var boundInputEvents = this.bindInputEvents.bind(this);
    boundInputEvents();
  };

  FilterCheckboxes.prototype.getCheckboxInput = function (el) {
    return el.querySelector('input')
  };

  FilterCheckboxes.prototype.bindInputEvents = function () {
    var $textbox = this.$textbox;
    var checkboxArr = this.checkboxArr.map(this.getCheckboxInput);

    $textbox.addEventListener('input', this.filterCheckboxes.bind(this));

    var boundUpdateAriaDescribedBy = this.updateAriaDescribedBy.bind(this);
    checkboxArr.forEach(chbxEl => chbxEl.addEventListener('change', boundUpdateAriaDescribedBy));
  };

  FilterCheckboxes.prototype.filterCheckboxes = function () {
    var $textbox = this.$textbox;
    var boundFilterCheckboxesArr = this.filterCheckboxesArr.bind(this);
    // filter the array of checkboxes
    var reducedArr = boundFilterCheckboxesArr($textbox.value);

    var boundUpdateAriaDescribedBy = this.updateAriaDescribedBy.bind(this);

    // show only those checkboxes remaining
    var boundDisplayMatchingCheckboxes = this.displayMatchingCheckboxes.bind(this);
    boundDisplayMatchingCheckboxes(reducedArr, boundUpdateAriaDescribedBy);
  };

  FilterCheckboxes.prototype.filterCheckboxesArr = function (query) {
    var checkboxArr = this.checkboxArr;
    return checkboxArr.filter(function (el) {
      const checkbox = el.querySelector('label');
      return checkbox.textContent.toLowerCase().indexOf(query.toLowerCase()) !== -1
    })
  };

  function setCheckboxDisplay (ckbx, displayValue) {
    ckbx.style.display = displayValue;
  }

  FilterCheckboxes.prototype.displayMatchingCheckboxes = function (ckbxArr, cb) {
    // hide all
    this.checkboxArr.forEach((ckbx) => setCheckboxDisplay(ckbx, 'none'));
    // re show those in filtered array
    ckbxArr.forEach((ckbx) => setCheckboxDisplay(ckbx, 'block'));

    if (cb) {
      cb();
    }
  };

  FilterCheckboxes.prototype.updateAriaDescribedBy = function () {
    var checkboxArr = this.checkboxArr;
    var displayedCheckboxes = checkboxArr.filter(chbx => !this.isDisplayNone(chbx));
    var checkedAndDisplayed = displayedCheckboxes.filter(chbx => this.isItemChecked(chbx));

    var boundGenerateAriaMessage = this.generateAriaMessage.bind(this);
    boundGenerateAriaMessage(displayedCheckboxes.length, checkedAndDisplayed.length);
  };

  FilterCheckboxes.prototype.generateAriaMessage = function (optionCount, selectedCount) {
    var ariaEl = this.ariaDescription;
    var optionStr = ariaEl.dataset.single;
    if (optionCount > 1) {
      optionStr = ariaEl.dataset.multiple;
    }

    ariaEl.textContent = optionCount + ' ' + optionStr + ', ' + selectedCount + ' ' + ariaEl.dataset.selected;
  };

  FilterCheckboxes.prototype.setupOptions = function (params) {
    params = params || {};
    this.listItemSelector = params.listItemSelector || '.govuk-checkboxes__item';
  };

  /*
    Selected counts for filter

    Used with the FilterGroup component to display the
    number of selected items in the filter group list.

  */

  function FilterGroupSelectedCounter ($module) {
    this.$module = $module;
    this.$fieldset = $module.querySelector('fieldset');
    this.$inputs = this.$fieldset.querySelectorAll('input');
  }

  FilterGroupSelectedCounter.prototype.init = function () {
    var $inputs = this.$inputs;

    // if no inputs then return
    if (!$inputs) {
      return
    }

    //
    var boundFetchCountElement = this.fetchCountElement.bind(this);
    this.countMessage = boundFetchCountElement();

    // if current count is 0 hide the message
    this.message_is_hidden = false;
    if (this.currentCount === 0) {
      this.hideCountMessage();
    }

    // Bind event changes to the textarea
    var boundChangeEvents = this.bindChangeEvents.bind(this);
    boundChangeEvents();

    return this
  };

  FilterGroupSelectedCounter.prototype.fetchCountElement = function () {
    var $module = this.$module;
    var countMessage = $module.querySelector('.dl-filter-group__selected-text');

    // if the count message doesn;t exist, create one
    if (!countMessage) {
      countMessage = this.createCountElement();
    }

    this.countElement = countMessage.querySelector('.dl-filter-group__selected-text__count');
    this.currentCount = parseInt(this.countElement.textContent);

    return countMessage
  };

  FilterGroupSelectedCounter.prototype.createCountElement = function () {
    var $module = this.$module;
    var $summary = $module.querySelector('.dl-filter-group__summary');
    var firstIcon = $summary.querySelector('svg');

    var countMessage = document.createElement('span');
    countMessage.classList.add('dl-filter-group__selected-text');
    countMessage.textContent = ' selected';
    firstIcon.insertAdjacentElement('beforebegin', countMessage);

    countMessage.insertAdjacentHTML('afterbegin', '<span class="dl-filter-group__selected-text__count">0</span>');

    return countMessage
  };

  FilterGroupSelectedCounter.prototype.bindChangeEvents = function () {
    var $inputs = this.$inputs;
    // console.log(this)
    $inputs.forEach(input => {
      input.addEventListener('change', this.updateCount.bind(this));
    });
  };

  FilterGroupSelectedCounter.prototype.updateCount = function () {
    var $fieldset = this.$fieldset;
    var count = $fieldset.querySelectorAll('input:checked').length;

    // if 0 hide
    if (count === 0) {
      this.countElement.textContent = 0;
      this.hideCountMessage();
    } else if (count !== this.currentCount) {
      // if changed update
      this.countElement.textContent = count;
      this.showCountMessage();
    }
    // if same, do nothing ----

    this.currentCount = count;
  };

  FilterGroupSelectedCounter.prototype.hideCountMessage = function () {
    this.countMessage.classList.add('govuk-visually-hidden');
    this.message_is_hidden = true;
  };

  FilterGroupSelectedCounter.prototype.showCountMessage = function () {
    this.countMessage.classList.remove('govuk-visually-hidden');
    this.message_is_hidden = false;
  };

  function HorizontalScrollableTable ($module) {
    this.$module = $module;
  }

  HorizontalScrollableTable.prototype.init = function () {
    this.data_table = this.$module.querySelector('table');

    // might be worth adding the shadows separately
    this.left_shadow = this.$module.querySelector('.dl-data-table-left-shadow');
    this.right_shadow = this.$module.querySelector('.dl-data-table-right-shadow');

    this.table_viewer = this.$module.querySelector('.wide-table');
    this.table_viewer.addEventListener('scroll', this.toggleShadows.bind(this));

    // trigger toggleShadow for set up
    this.toggleShadows();
  };

  HorizontalScrollableTable.prototype.toggleShadows = function () {
    function scrolledRight (containedEl, viewerEl) {
      return (
        containedEl.offsetWidth - (viewerEl.scrollLeft + viewerEl.offsetWidth)
      )
    }

    this.left_shadow.classList.toggle(
      'visible',
      scrolledRight(this.data_table, this.table_viewer) <
        this.data_table.offsetWidth - this.table_viewer.offsetWidth
    );

    this.right_shadow.classList.toggle(
      'visible',
      this.table_viewer.scrollLeft <
        this.data_table.offsetWidth - this.table_viewer.offsetWidth
    );

    setTimeout(
      function () {
        this.left_shadow.classList.add('with-transition');
        this.right_shadow.classList.add('with-transition');
      }.bind(this),
      2000
    );
  };

  function convertNodeListToArray (nl) {
    return Array.prototype.slice.call(nl)
  }

  // Currently works by looking for all lists and list items on the page, not confined to a section of a page.
  // We might want to change this so that it is more flexible.
  // Is there a situation where we need more than one list search on a page?

  // similar to
  // https://github.com/alphagov/collections/blob/e1f3c74facd889426d24ac730ed0057aa64e2801/app/assets/javascripts/organisation-list-filter.js
  function ListFilter ($form) {
    this.$form = $form;
    this.filterTimeout = null;
    this.$noMatches = document.querySelector('.dl-list-filter__no-filter-match');
  }

  ListFilter.prototype.init = function (params) {
    this.setupOptions(params);
    const $form = this.$form;
    // Form should only appear if the JS is working
    $form.classList.add('list-filter__form--active');

    // We don't want the form to submit/refresh the page on enter key
    $form.addEventListener('submit', function () { return false });

    const $input = $form.querySelector('input');
    const boundFilterViaTimeout = this.filterViaTimeout.bind(this);
    $input.addEventListener('keyup', boundFilterViaTimeout);

    // make sure no matches message is initially hidden
    this.$noMatches.classList.add('js-hidden');
  };

  ListFilter.prototype.filterViaTimeout = function (e) {
    clearTimeout(this.filterTimeout);

    const boundListFilter = this.ListFilter.bind(this);
    this.filterTimeout = setTimeout(function () {
      boundListFilter(e);
    }, 200);
  };

  ListFilter.prototype.ListFilter = function (e) {
    const itemsToFilter = convertNodeListToArray(document.querySelectorAll('[data-filter="item"]'));
    const listsToFilter = convertNodeListToArray(document.querySelectorAll('[data-filter="list"]'));
    const searchTerm = e.target.value;

    // set a class if a search/filter is in progress
    this.setActiveClasses(listsToFilter, searchTerm);

    const boundMatchSearchTerm = this.matchSearchTerm.bind(this);
    itemsToFilter
      .filter(function ($item) {
        return boundMatchSearchTerm($item, searchTerm)
      })
      .forEach(function (item) {
        item.classList.add('js-hidden');
      });

    this.updateListCounts(listsToFilter);
  };

  ListFilter.prototype.termToMatchOn = function (item) {
    const toConsider = item.querySelectorAll('[data-filter="match-content"]');
    if (toConsider.length) {
      const toConsiderArr = convertNodeListToArray(toConsider);
      const toConsiderStrs = toConsiderArr.map(function (el) {
        return el.textContent
      });
      return toConsiderStrs.join(';')
    }
    return item.querySelector('a').textContent
  };

  ListFilter.prototype.matchSearchTerm = function (item, term) {
    // const itemLabels = item.dataset.filterItemLabels
    const contentToMatchOn = this.termToMatchOn(item);
    item.classList.remove('js-hidden');
    var searchTermRegexp = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
    if (searchTermRegexp.exec(contentToMatchOn) !== null) {
      return false
    }
    return true
  };

  ListFilter.prototype.setActiveClasses = function(lists, searchTerm) {
    lists.forEach(list => {
      if (searchTerm !== '') {
        list.classList.add(this.list_filtered_class);
      } else {
        list.classList.remove(this.list_filtered_class);
      }
    });
  };

  ListFilter.prototype.updateListCounts = function (lists) {
    var totalMatches = 0;
    const list_section_selector = this.list_section_selector;
    const count_wrapper_selector = this.count_wrapper_selector;

    lists.forEach(function (list) {
      var matchingCount = list.querySelectorAll('[data-filter="item"]:not(.js-hidden)').length;
      var listSection = list.closest(list_section_selector);
      var countWrapper = listSection.querySelector(count_wrapper_selector);
      var listCount = countWrapper.querySelector('.js-list-filter__count');
      var accessibleListCount = countWrapper.querySelector('.js-accessible-list-filter__count');

      // show/hide sections with matching items
      if (matchingCount > 0) {
        listSection.classList.remove('js-hidden');
        listCount.textContent = matchingCount;
        accessibleListCount.textContent = matchingCount;
      } else {
        listSection.classList.add('js-hidden');
      }

      totalMatches += matchingCount;

      var filteredEvent = new CustomEvent('list:filtered');
      list.dispatchEvent(filteredEvent);
    });

    // if no results show message
    if (this.$noMatches) {
      if (totalMatches === 0) {
        this.$noMatches.classList.remove('js-hidden');
      } else {
        this.$noMatches.classList.add('js-hidden');
      }
    }
  };

  ListFilter.prototype.setupOptions = function (params) {
    params = params || {};
    this.list_section_selector = params.list_section_selector || '.dl-list-filter__count';
    this.count_wrapper_selector = params.count_wrapper_selector || '.dl-list-filter__count__wrapper';
    this.list_filtered_class = params.list_filtered_class || 'dl-list-filter__filtered-listed';
  };

  function nodeListForEach (nodes, callback) {
    if (window.NodeList.prototype.forEach) {
      return nodes.forEach(callback)
    }
    for (var i = 0; i < nodes.length; i++) {
      callback.call(window, nodes[i], i, nodes);
    }
  }

  function SubNavTabs ($module) {
    this.$module = $module;
    this.$body = document.querySelector('body');

    this.keys = { left: 37, right: 39, up: 38, down: 40 };
    this.jsHiddenClass = 'govuk-tabs__panel--hidden';
  }

  SubNavTabs.prototype.init = function (params) {
    this.setupOptions(params);
    this.$tabs = this.$module.querySelectorAll(this.subNavTabsSelector);

    if (typeof window.matchMedia === 'function') {
      this.setupResponsiveChecks();
    } else {
      this.setup();
    }

    return this
  };

  SubNavTabs.prototype.setupResponsiveChecks = function () {
    this.mql = window.matchMedia('(min-width: 40.0625em)');
    this.mql.addListener(this.checkMode.bind(this));
    this.checkMode();
  };

  SubNavTabs.prototype.checkMode = function () {
    if (this.mql.matches) {
      this.setup();
    } else {
      this.teardown();
    }
  };

  SubNavTabs.prototype.setup = function () {
    var $module = this.$module;
    var $tabs = this.$tabs;
    var $tabList = $module.querySelector(this.subNavListSelector);
    var $tabListItems = $module.querySelectorAll(this.subNavListItemSelector);

    if (!$tabs || !$tabList || !$tabListItems) {
      return
    }

    $tabList.setAttribute('role', 'tablist');

    nodeListForEach($tabListItems, function ($item) {
      $item.setAttribute('role', 'presentation');
    });

    nodeListForEach($tabs, function ($tab) {
      // Set HTML attributes
      this.setAttributes($tab);

      // Save bounded functions to use when removing event listeners during teardown
      $tab.boundTabClick = this.onTabClick.bind(this);
      $tab.boundTabKeydown = this.onTabKeydown.bind(this);

      // Handle events
      $tab.addEventListener('click', $tab.boundTabClick, true);
      $tab.addEventListener('keydown', $tab.boundTabKeydown, true);

      // Remove old active panels
      this.hideTab($tab);
    }.bind(this));

    // Show either the active tab according to the URL's hash or the first tab
    var $activeTab = this.getTab(window.location.hash) || this.$tabs[0];
    this.showTab($activeTab);

    // Handle hashchange events
    $module.boundOnHashChange = this.onHashChange.bind(this);
    window.addEventListener('hashchange', $module.boundOnHashChange, true);

    // Add class to acknowledge module has been initiated
    this.$body.classList.add(this.subNavActivatedClass);
  };

  SubNavTabs.prototype.teardown = function () {
    var $module = this.$module;
    var $tabs = this.$tabs;
    var $tabList = $module.querySelector(this.subNavListSelector);
    var $tabListItems = $module.querySelectorAll(this.subNavListItemSelector);

    if (!$tabs || !$tabList || !$tabListItems) {
      return
    }

    $tabList.removeAttribute('role');

    nodeListForEach($tabListItems, function ($item) {
      $item.removeAttribute('role', 'presentation');
    });

    nodeListForEach($tabs, function ($tab) {
      // Remove events
      $tab.removeEventListener('click', $tab.boundTabClick, true);
      $tab.removeEventListener('keydown', $tab.boundTabKeydown, true);

      // Unset HTML attributes
      this.unsetAttributes($tab);
    }.bind(this));

    // Remove hashchange event handler
    window.removeEventListener('hashchange', $module.boundOnHashChange, true);

    // Remove class acknowledging module was initiated
    this.$body.classList.remove(this.subNavActivatedClass);
  };

  SubNavTabs.prototype.onHashChange = function (e) {
    var hash = window.location.hash;
    // if user hits back button to none hashed state then need to show the first tab
    var $tabWithHash = this.getTab(hash) || this.$tabs[0];

    // Prevent changing the hash
    if (this.changingHash) {
      this.changingHash = false;
      return
    }

    // Show either the active tab according to the URL's hash or the first tab
    var $previousTab = this.getCurrentTab();

    this.hideTab($previousTab);
    this.showTab($tabWithHash);
    $tabWithHash.focus();
  };

  SubNavTabs.prototype.hideTab = function ($tab) {
    this.unhighlightTab($tab);
    this.hidePanel($tab);
  };

  SubNavTabs.prototype.showTab = function ($tab) {
    this.highlightTab($tab);
    this.showPanel($tab);
  };

  SubNavTabs.prototype.getTab = function (hash) {
    return this.$module.querySelector(`${this.subNavTabsSelector}[href="${hash}"]`)
  };

  SubNavTabs.prototype.setAttributes = function ($tab) {
    // set tab attributes
    var panelId = this.getHref($tab).slice(1);
    $tab.setAttribute('id', 'tab_' + panelId);
    $tab.setAttribute('role', 'tab');
    $tab.setAttribute('aria-controls', panelId);
    $tab.setAttribute('aria-selected', 'false');
    $tab.setAttribute('tabindex', '-1');

    // set panel attributes
    var $panel = this.getPanel($tab);
    $panel.setAttribute('role', 'tabpanel');
    $panel.setAttribute('aria-labelledby', $tab.id);
    $panel.classList.add(this.jsHiddenClass);
  };

  SubNavTabs.prototype.unsetAttributes = function ($tab) {
    // unset tab attributes
    $tab.removeAttribute('id');
    $tab.removeAttribute('role');
    $tab.removeAttribute('aria-controls');
    $tab.removeAttribute('aria-selected');
    $tab.removeAttribute('tabindex');

    // unset panel attributes
    var $panel = this.getPanel($tab);
    $panel.removeAttribute('role');
    $panel.removeAttribute('aria-labelledby');
    $panel.classList.remove(this.jsHiddenClass);
  };

  SubNavTabs.prototype.onTabClick = function (e) {
    const tabClass = this.subNavTabsSelector.replace('.', '');
    if (!e.target.classList.contains(tabClass)) {
    // Allow events on child DOM elements to bubble up to tab parent
      return false
    }
    e.preventDefault();
    var $newTab = e.target;
    var $currentTab = this.getCurrentTab();
    this.hideTab($currentTab);
    this.showTab($newTab);
    this.createHistoryEntry($newTab);
  };

  SubNavTabs.prototype.createHistoryEntry = function ($tab) {
    var $panel = this.getPanel($tab);

    // Save and restore the id
    // so the page doesn't jump when a user clicks a tab (which changes the hash)
    var id = $panel.id;
    $panel.id = '';
    this.changingHash = true;
    window.location.hash = this.getHref($tab).slice(1);
    $panel.id = id;
  };

  SubNavTabs.prototype.onTabKeydown = function (e) {
    switch (e.keyCode) {
      case this.keys.left:
      case this.keys.up:
        this.activatePreviousTab();
        e.preventDefault();
        break
      case this.keys.right:
      case this.keys.down:
        this.activateNextTab();
        e.preventDefault();
        break
    }
  };

  SubNavTabs.prototype.activateNextTab = function () {
    var currentTab = this.getCurrentTab();
    var nextTabListItem = currentTab.parentNode.nextElementSibling;
    if (nextTabListItem) {
      var nextTab = nextTabListItem.querySelector(this.subNavTabsSelector);
    }
    if (nextTab) {
      this.hideTab(currentTab);
      this.showTab(nextTab);
      nextTab.focus();
      this.createHistoryEntry(nextTab);
    }
  };

  SubNavTabs.prototype.activatePreviousTab = function () {
    var currentTab = this.getCurrentTab();
    var previousTabListItem = currentTab.parentNode.previousElementSibling;
    if (previousTabListItem) {
      var previousTab = previousTabListItem.querySelector(this.subNavTabsSelector);
    }
    if (previousTab) {
      this.hideTab(currentTab);
      this.showTab(previousTab);
      previousTab.focus();
      this.createHistoryEntry(previousTab);
    }
  };

  SubNavTabs.prototype.getPanel = function ($tab) {
    var $panel = this.$module.querySelector(this.getHref($tab));
    return $panel
  };

  SubNavTabs.prototype.showPanel = function ($tab) {
    var $panel = this.getPanel($tab);
    $panel.classList.remove(this.jsHiddenClass);
  };

  SubNavTabs.prototype.hidePanel = function (tab) {
    var $panel = this.getPanel(tab);
    $panel.classList.add(this.jsHiddenClass);
  };

  SubNavTabs.prototype.unhighlightTab = function ($tab) {
    $tab.setAttribute('aria-selected', 'false');
    $tab.parentNode.classList.remove(this.subNavTabSelectedClass);
    $tab.setAttribute('tabindex', '-1');
  };

  SubNavTabs.prototype.highlightTab = function ($tab) {
    $tab.setAttribute('aria-selected', 'true');
    $tab.parentNode.classList.add(this.subNavTabSelectedClass);
    $tab.setAttribute('tabindex', '0');
  };

  SubNavTabs.prototype.getCurrentTab = function () {
    const selector = `.${this.subNavTabSelectedClass} ${this.subNavTabsSelector}`;
    return this.$module.querySelector(selector)
  };

  // this is because IE doesn't always return the actual value but a relative full path
  // should be a utility function most prob
  // http://labs.thesedays.com/blog/2010/01/08/getting-the-href-value-with-jquery-in-ie/
  SubNavTabs.prototype.getHref = function ($tab) {
    var href = $tab.getAttribute('href');
    var hash = href.slice(href.indexOf('#'), href.length);
    return hash
  };

  SubNavTabs.prototype.setupOptions = function (params) {
    params = params || {};
    this.subNavActivatedClass = params.subNavActivatedClass || 'dl-subnav--init';
    this.subNavListSelector = params.subNavListSelector || '.dl-subnav__list';
    this.subNavListItemSelector = params.subNavListItemSelector || '.dl-subnav__list-item';
    this.subNavTabsSelector = params.subNavTabsSelector || '.dl-subnav__list-item__link';
    this.subNavTabSelectedClass = params.subNavTabSelectedClass || 'dl-subnav__list-item--selected';
    this.hideClass = params.hideClass || 'back-to-top--hidden';
    this.fixClass = params.fixClass || 'back-to-top--fixed';
  };

  function polyfill (options) {
    // polyfill for browsers without NodeList forEach method
    if (window.NodeList && !window.NodeList.prototype.forEach) {
      window.NodeList.prototype.forEach = window.Array.prototype.forEach;
    }
  }

  function initAll (options) {
    // Set the options to an empty object by default if no options are passed.
    options = typeof options !== 'undefined' ? options : {};

    // Allow the user to initialise Digital Land Frontend in only certain sections of the page
    // Defaults to the entire document if nothing is set.
    var scope = typeof options.scope !== 'undefined' ? options.scope : document;

    // load required polyfills
    polyfill();

    var $bttButtons = convertNodeListToArray$1(scope.querySelectorAll('[data-module="dl-back-to-top-button"]'));
    $bttButtons.forEach(function ($button) {
      new BackToTop($button).init();
    });

    var $formToFilterList = scope.querySelector('[data-module="dl-list-filter-form"]');
    if ($formToFilterList) {
      new ListFilter($formToFilterList).init();
    }

    var $filters = scope.querySelectorAll('[data-module="selected-counter"]');
    $filters.forEach(function($filter) {
      new FilterGroupSelectedCounter($filter).init();
    });

    var $filterCheckboxes = scope.querySelectorAll('[data-module="filter-checkboxes"]');
    $filterCheckboxes.forEach(function($el) {
      new FilterCheckboxes($el).init();
    });

    var $subNavTabs = scope.querySelector('[data-module="dl-subnav"]');
    // check element was found before initialising
    if ($subNavTabs) {
      new SubNavTabs($subNavTabs).init({});
    }

    var $scrollableTables = scope.querySelectorAll('[data-module="scrollable-table"]');
    $scrollableTables.forEach(function($table) {
      new HorizontalScrollableTable($table).init();
    });
  }

  exports.BackToTop = BackToTop;
  exports.FilterCheckboxes = FilterCheckboxes;
  exports.FilterGroupSelectedCounter = FilterGroupSelectedCounter;
  exports.HorizontalScrollableTable = HorizontalScrollableTable;
  exports.ListFilter = ListFilter;
  exports.SubNavTabs = SubNavTabs;
  exports.initAll = initAll;
  exports.polyfill = polyfill;

  Object.defineProperty(exports, '__esModule', { value: true });

}));
