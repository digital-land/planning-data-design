(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('govuk-frontend')) :
  typeof define === 'function' && define.amd ? define(['exports', 'govuk-frontend'], factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.MOJFrontend = global.MOJFrontend || {}, global.GOVUKFrontend));
})(this, (function (exports, govukFrontend) { 'use strict';

  /*
   * This variable is automatically overwritten during builds and releases.
   * It doesn't need to be updated manually.
   */

  /**
   * MoJ Frontend release version
   *
   * {@link https://github.com/ministryofjustice/moj-frontend/releases}
   */
  const version = '5.1.3';

  class AddAnother extends govukFrontend.Component {
    /**
     * @param {Element | null} $root - HTML element to use for add another
     */
    constructor($root) {
      super($root);
      this.$root.addEventListener('click', this.onRemoveButtonClick.bind(this));
      this.$root.addEventListener('click', this.onAddButtonClick.bind(this));
      const $buttons = this.$root.querySelectorAll('.moj-add-another__add-button, moj-add-another__remove-button');
      $buttons.forEach($button => {
        if (!($button instanceof HTMLButtonElement)) {
          return;
        }
        $button.type = 'button';
      });
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    onAddButtonClick(event) {
      const $button = event.target;
      if (!$button || !($button instanceof HTMLButtonElement) || !$button.classList.contains('moj-add-another__add-button')) {
        return;
      }
      const $items = this.getItems();
      const $item = this.getNewItem();
      if (!$item || !($item instanceof HTMLElement)) {
        return;
      }
      this.updateAttributes($item, $items.length);
      this.resetItem($item);
      const $firstItem = $items[0];
      if (!this.hasRemoveButton($firstItem)) {
        this.createRemoveButton($firstItem);
      }
      $items[$items.length - 1].after($item);
      const $input = $item.querySelector('input, textarea, select');
      if ($input && $input instanceof HTMLInputElement) {
        $input.focus();
      }
    }

    /**
     * @param {HTMLElement} $item - Add another item
     */
    hasRemoveButton($item) {
      return $item.querySelectorAll('.moj-add-another__remove-button').length;
    }
    getItems() {
      if (!this.$root) {
        return [];
      }
      const $items = Array.from(this.$root.querySelectorAll('.moj-add-another__item'));
      return $items.filter(item => item instanceof HTMLElement);
    }
    getNewItem() {
      const $items = this.getItems();
      const $item = $items[0].cloneNode(true);
      if (!$item || !($item instanceof HTMLElement)) {
        return;
      }
      if (!this.hasRemoveButton($item)) {
        this.createRemoveButton($item);
      }
      return $item;
    }

    /**
     * @param {HTMLElement} $item - Add another item
     * @param {number} index - Add another item index
     */
    updateAttributes($item, index) {
      $item.querySelectorAll('[data-name]').forEach($input => {
        if (!this.isValidInputElement($input)) {
          return;
        }
        const name = $input.getAttribute('data-name') || '';
        const id = $input.getAttribute('data-id') || '';
        const originalId = $input.id;
        $input.name = name.replace(/%index%/, `${index}`);
        $input.id = id.replace(/%index%/, `${index}`);
        const $label = $input.parentElement.querySelector('label') || $input.closest('label') || $item.querySelector(`[for="${originalId}"]`);
        if ($label && $label instanceof HTMLLabelElement) {
          $label.htmlFor = $input.id;
        }
      });
    }

    /**
     * @param {HTMLElement} $item - Add another item
     */
    createRemoveButton($item) {
      const $button = document.createElement('button');
      $button.type = 'button';
      $button.classList.add('govuk-button', 'govuk-button--secondary', 'moj-add-another__remove-button');
      $button.textContent = 'Remove';
      $item.append($button);
    }

    /**
     * @param {HTMLElement} $item - Add another item
     */
    resetItem($item) {
      $item.querySelectorAll('[data-name], [data-id]').forEach($input => {
        if (!this.isValidInputElement($input)) {
          return;
        }
        if ($input instanceof HTMLSelectElement) {
          $input.selectedIndex = -1;
          $input.value = '';
        } else if ($input instanceof HTMLTextAreaElement) {
          $input.value = '';
        } else {
          switch ($input.type) {
            case 'checkbox':
            case 'radio':
              $input.checked = false;
              break;
            default:
              $input.value = '';
          }
        }
      });
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    onRemoveButtonClick(event) {
      const $button = event.target;
      if (!$button || !($button instanceof HTMLButtonElement) || !$button.classList.contains('moj-add-another__remove-button')) {
        return;
      }
      $button.closest('.moj-add-another__item').remove();
      const $items = this.getItems();
      if ($items.length === 1) {
        $items[0].querySelector('.moj-add-another__remove-button').remove();
      }
      $items.forEach(($item, index) => {
        this.updateAttributes($item, index);
      });
      this.focusHeading();
    }
    focusHeading() {
      const $heading = this.$root.querySelector('.moj-add-another__heading');
      if ($heading && $heading instanceof HTMLElement) {
        $heading.focus();
      }
    }

    /**
     * @param {Element} $input - the input to validate
     */
    isValidInputElement($input) {
      return $input instanceof HTMLInputElement || $input instanceof HTMLSelectElement || $input instanceof HTMLTextAreaElement;
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }
  AddAnother.moduleName = 'moj-add-another';

  /**
   * GOV.UK Frontend helpers
   *
   * @todo Import from GOV.UK Frontend
   */

  /**
   * Move focus to element
   *
   * Sets tabindex to -1 to make the element programmatically focusable,
   * but removes it on blur as the element doesn't need to be focused again.
   *
   * @template {HTMLElement} FocusElement
   * @param {FocusElement} $element - HTML element
   * @param {object} [options] - Handler options
   * @param {function(this: FocusElement): void} [options.onBeforeFocus] - Callback before focus
   * @param {function(this: FocusElement): void} [options.onBlur] - Callback on blur
   */
  function setFocus($element, options = {}) {
    var _options$onBeforeFocu;
    const isFocusable = $element.getAttribute('tabindex');
    if (!isFocusable) {
      $element.setAttribute('tabindex', '-1');
    }

    /**
     * Handle element focus
     */
    function onFocus() {
      $element.addEventListener('blur', onBlur, {
        once: true
      });
    }

    /**
     * Handle element blur
     */
    function onBlur() {
      var _options$onBlur;
      (_options$onBlur = options.onBlur) == null || _options$onBlur.call($element);
      if (!isFocusable) {
        $element.removeAttribute('tabindex');
      }
    }

    // Add listener to reset element on blur, after focus
    $element.addEventListener('focus', onFocus, {
      once: true
    });

    // Focus element
    (_options$onBeforeFocu = options.onBeforeFocus) == null || _options$onBeforeFocu.call($element);
    $element.focus();
  }

  /**
   * @param {Element} $element - Element to remove attribute value from
   * @param {string} attr - Attribute name
   * @param {string} value - Attribute value
   */
  function removeAttributeValue($element, attr, value) {
    let re, m;
    if ($element.getAttribute(attr)) {
      if ($element.getAttribute(attr) === value) {
        $element.removeAttribute(attr);
      } else {
        re = new RegExp(`(^|\\s)${value}(\\s|$)`);
        m = $element.getAttribute(attr).match(re);
        if (m && m.length === 3) {
          $element.setAttribute(attr, $element.getAttribute(attr).replace(re, m[1] && m[2] ? ' ' : ''));
        }
      }
    }
  }

  /**
   * @param {Element} $element - Element to add attribute value to
   * @param {string} attr - Attribute name
   * @param {string} value - Attribute value
   */
  function addAttributeValue($element, attr, value) {
    let re;
    if (!$element.getAttribute(attr)) {
      $element.setAttribute(attr, value);
    } else {
      re = new RegExp(`(^|\\s)${value}(\\s|$)`);
      if (!re.test($element.getAttribute(attr))) {
        $element.setAttribute(attr, `${$element.getAttribute(attr)} ${value}`);
      }
    }
  }

  /**
   * Find an elements preceding sibling
   *
   * Utility function to find an elements previous sibling matching the provided
   * selector.
   *
   * @param {Element | null} $element - Element to find siblings for
   * @param {string} [selector] - selector for required sibling
   */
  function getPreviousSibling($element, selector) {
    if (!$element || !($element instanceof HTMLElement)) {
      return;
    }

    // Get the previous sibling element
    let $sibling = $element.previousElementSibling;

    // If the sibling matches our selector, use it
    // If not, jump to the next sibling and continue the loop
    while ($sibling) {
      if ($sibling.matches(selector)) return $sibling;
      $sibling = $sibling.previousElementSibling;
    }
  }

  /**
   * @param {Element | null} $element
   * @param {string} [selector]
   */
  function findNearestMatchingElement($element, selector) {
    // If no element or selector is provided, return
    if (!$element || !($element instanceof HTMLElement) || false) {
      return;
    }

    // Start with the current element
    let $currentElement = $element;
    while ($currentElement) {
      // First check the current element
      if ($currentElement.matches(selector)) {
        return $currentElement;
      }

      // Check all previous siblings
      let $sibling = $currentElement.previousElementSibling;
      while ($sibling) {
        // Check if the sibling itself is a heading
        if ($sibling.matches(selector)) {
          return $sibling;
        }
        $sibling = $sibling.previousElementSibling;
      }

      // If no match found in siblings, move up to parent
      $currentElement = $currentElement.parentElement;
    }
  }

  /**
   * @augments {ConfigurableComponent<AlertConfig>}
   */
  class Alert extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for alert
     * @param {AlertConfig} [config] - Alert config
     */
    constructor($root, config = {}) {
      super($root, config);

      /**
       * Focus the alert
       *
       * If `role="alert"` is set, focus the element to help some assistive
       * technologies prioritise announcing it.
       *
       * You can turn off the auto-focus functionality by setting
       * `data-disable-auto-focus="true"` in the component HTML. You might wish to
       * do this based on user research findings, or to avoid a clash with another
       * element which should be focused when the page loads.
       */
      if (this.$root.getAttribute('role') === 'alert' && !this.config.disableAutoFocus) {
        setFocus(this.$root);
      }
      this.$dismissButton = this.$root.querySelector('.moj-alert__dismiss');
      if (this.config.dismissible && this.$dismissButton) {
        this.$dismissButton.innerHTML = this.config.dismissText;
        this.$dismissButton.removeAttribute('hidden');
        this.$root.addEventListener('click', event => {
          if (event.target instanceof Node && this.$dismissButton.contains(event.target)) {
            this.dimiss();
          }
        });
      }
    }

    /**
     * Handle dismissing the alert
     */
    dimiss() {
      let $elementToRecieveFocus;

      // If a selector has been provided, attempt to find that element
      if (this.config.focusOnDismissSelector) {
        $elementToRecieveFocus = document.querySelector(this.config.focusOnDismissSelector);
      }

      // Is the next sibling another alert
      if (!$elementToRecieveFocus) {
        const $nextSibling = this.$root.nextElementSibling;
        if ($nextSibling && $nextSibling.matches('.moj-alert')) {
          $elementToRecieveFocus = $nextSibling;
        }
      }

      // Else try to find any preceding sibling alert or heading
      if (!$elementToRecieveFocus) {
        $elementToRecieveFocus = getPreviousSibling(this.$root, '.moj-alert, h1, h2, h3, h4, h5, h6');
      }

      // Else find the closest ancestor heading, or fallback to main, or last resort
      // use the body element
      if (!$elementToRecieveFocus) {
        $elementToRecieveFocus = findNearestMatchingElement(this.$root, 'h1, h2, h3, h4, h5, h6, main, body');
      }

      // If we have an element, place focus on it
      if ($elementToRecieveFocus instanceof HTMLElement) {
        setFocus($elementToRecieveFocus);
      }

      // Remove the alert
      this.$root.remove();
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }

  /**
   * @typedef {object} AlertConfig
   * @property {boolean} [dismissible=false] - Can the alert be dismissed by the user
   * @property {string} [dismissText=Dismiss] - the label text for the dismiss button
   * @property {boolean} [disableAutoFocus=false] - whether the alert will be autofocused
   * @property {string} [focusOnDismissSelector] - CSS Selector for element to be focused on dismiss
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */
  Alert.moduleName = 'moj-alert';
  /**
   * Alert default config
   *
   * @type {AlertConfig}
   */
  Alert.defaults = Object.freeze({
    dismissible: false,
    dismissText: 'Dismiss',
    disableAutoFocus: false
  });
  /**
   * Alert config schema
   *
   * @satisfies {Schema<AlertConfig>}
   */
  Alert.schema = Object.freeze(/** @type {const} */{
    properties: {
      dismissible: {
        type: 'boolean'
      },
      dismissText: {
        type: 'string'
      },
      disableAutoFocus: {
        type: 'boolean'
      },
      focusOnDismissSelector: {
        type: 'string'
      }
    }
  });

  /**
   * @augments {ConfigurableComponent<ButtonMenuConfig>}
   */
  class ButtonMenu extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for button menu
     * @param {ButtonMenuConfig} [config] - Button menu config
     */
    constructor($root, config = {}) {
      super($root, config);

      // If only one button is provided, don't initiate a menu and toggle button
      // if classes have been provided for the toggleButton, apply them to the single item
      if (this.$root.children.length === 1) {
        const $button = this.$root.children[0];
        $button.classList.forEach(className => {
          if (className.startsWith('govuk-button-')) {
            $button.classList.remove(className);
          }
          $button.classList.remove('moj-button-menu__item');
          $button.classList.add('moj-button-menu__single-button');
        });
        if (this.config.buttonClasses) {
          $button.classList.add(...this.config.buttonClasses.split(' '));
        }
      }
      // Otherwise initialise a button menu
      if (this.$root.children.length > 1) {
        this.initMenu();
      }
    }
    initMenu() {
      this.$menu = this.createMenu();
      this.$root.insertAdjacentHTML('afterbegin', this.toggleTemplate());
      this.setupMenuItems();
      this.$menuToggle = this.$root.querySelector(':scope > button');
      this.$items = this.$menu.querySelectorAll('a, button');
      this.$menuToggle.addEventListener('click', event => {
        this.toggleMenu(event);
      });
      this.$root.addEventListener('keydown', event => {
        this.handleKeyDown(event);
      });
      document.addEventListener('click', event => {
        if (event.target instanceof Node && !this.$root.contains(event.target)) {
          this.closeMenu(false);
        }
      });
    }
    createMenu() {
      const $menu = document.createElement('ul');
      $menu.setAttribute('role', 'list');
      $menu.hidden = true;
      $menu.classList.add('moj-button-menu__wrapper');
      if (this.config.alignMenu === 'right') {
        $menu.classList.add('moj-button-menu__wrapper--right');
      }
      this.$root.appendChild($menu);
      while (this.$root.firstChild !== $menu) {
        $menu.appendChild(this.$root.firstChild);
      }
      return $menu;
    }
    setupMenuItems() {
      Array.from(this.$menu.children).forEach($menuItem => {
        // wrap item in li tag
        const $listItem = document.createElement('li');
        this.$menu.insertBefore($listItem, $menuItem);
        $listItem.appendChild($menuItem);
        $menuItem.setAttribute('tabindex', '-1');
        if ($menuItem.tagName === 'BUTTON') {
          $menuItem.setAttribute('type', 'button');
        }
        $menuItem.classList.forEach(className => {
          if (className.startsWith('govuk-button')) {
            $menuItem.classList.remove(className);
          }
        });

        // add a slight delay after click before closing the menu, makes it *feel* better
        $menuItem.addEventListener('click', () => {
          setTimeout(() => {
            this.closeMenu(false);
          }, 50);
        });
      });
    }
    toggleTemplate() {
      return `
    <button type="button" class="govuk-button moj-button-menu__toggle-button ${this.config.buttonClasses || ''}" aria-haspopup="true" aria-expanded="false">
      <span>
       ${this.config.buttonText}
       <svg width="11" height="5" viewBox="0 0 11 5"  xmlns="http://www.w3.org/2000/svg">
         <path d="M5.5 0L11 5L0 5L5.5 0Z" fill="currentColor"/>
       </svg>
      </span>
    </button>`;
    }

    /**
     * @returns {boolean}
     */
    isOpen() {
      return this.$menuToggle.getAttribute('aria-expanded') === 'true';
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    toggleMenu(event) {
      event.preventDefault();

      // If menu is triggered with mouse don't move focus to first item
      const keyboardEvent = event.detail === 0;
      const focusIndex = keyboardEvent ? 0 : -1;
      if (this.isOpen()) {
        this.closeMenu();
      } else {
        this.openMenu(focusIndex);
      }
    }

    /**
     * Opens the menu and optionally sets the focus to the item with given index
     *
     * @param {number} focusIndex - The index of the item to focus
     */
    openMenu(focusIndex = 0) {
      this.$menu.hidden = false;
      this.$menuToggle.setAttribute('aria-expanded', 'true');
      if (focusIndex !== -1) {
        this.focusItem(focusIndex);
      }
    }

    /**
     * Closes the menu and optionally returns focus back to menuToggle
     *
     * @param {boolean} moveFocus - whether to return focus to the toggle button
     */
    closeMenu(moveFocus = true) {
      this.$menu.hidden = true;
      this.$menuToggle.setAttribute('aria-expanded', 'false');
      if (moveFocus) {
        this.$menuToggle.focus();
      }
    }

    /**
     * Focuses the menu item at the specified index
     *
     * @param {number} index - the index of the item to focus
     */
    focusItem(index) {
      if (index >= this.$items.length) index = 0;
      if (index < 0) index = this.$items.length - 1;
      const $menuItem = this.$items.item(index);
      if ($menuItem) {
        $menuItem.focus();
      }
    }
    currentFocusIndex() {
      const $activeElement = document.activeElement;
      const $menuItems = Array.from(this.$items);
      return ($activeElement instanceof HTMLAnchorElement || $activeElement instanceof HTMLButtonElement) && $menuItems.indexOf($activeElement);
    }

    /**
     * @param {KeyboardEvent} event - Keydown event
     */
    handleKeyDown(event) {
      if (event.target === this.$menuToggle) {
        switch (event.key) {
          case 'ArrowDown':
            event.preventDefault();
            this.openMenu();
            break;
          case 'ArrowUp':
            event.preventDefault();
            this.openMenu(this.$items.length - 1);
            break;
        }
      }
      if (event.target instanceof Node && this.$menu.contains(event.target) && this.isOpen()) {
        switch (event.key) {
          case 'ArrowDown':
            event.preventDefault();
            if (this.currentFocusIndex() !== -1) {
              this.focusItem(this.currentFocusIndex() + 1);
            }
            break;
          case 'ArrowUp':
            event.preventDefault();
            if (this.currentFocusIndex() !== -1) {
              this.focusItem(this.currentFocusIndex() - 1);
            }
            break;
          case 'Home':
            event.preventDefault();
            this.focusItem(0);
            break;
          case 'End':
            event.preventDefault();
            this.focusItem(this.$items.length - 1);
            break;
        }
      }
      if (event.key === 'Escape' && this.isOpen()) {
        this.closeMenu();
      }
      if (event.key === 'Tab' && this.isOpen()) {
        this.closeMenu(false);
      }
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }

  /**
   * @typedef {object} ButtonMenuConfig
   * @property {string} [buttonText='Actions'] - Label for the toggle button
   * @property {"left" | "right"} [alignMenu='left'] - the alignment of the menu
   * @property {string} [buttonClasses='govuk-button--secondary'] - css classes applied to the toggle button
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */
  ButtonMenu.moduleName = 'moj-button-menu';
  /**
   * Button menu config
   *
   * @type {ButtonMenuConfig}
   */
  ButtonMenu.defaults = Object.freeze({
    buttonText: 'Actions',
    alignMenu: 'left',
    buttonClasses: ''
  });
  /**
   * Button menu config schema
   *
   * @type {Schema<ButtonMenuConfig>}
   */
  ButtonMenu.schema = Object.freeze(/** @type {const} */{
    properties: {
      buttonText: {
        type: 'string'
      },
      buttonClasses: {
        type: 'string'
      },
      alignMenu: {
        type: 'string'
      }
    }
  });

  /**
   * @augments {ConfigurableComponent<DatePickerConfig>}
   */
  class DatePicker extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for date picker
     * @param {DatePickerConfig} [config] - Date picker config
     */
    constructor($root, config = {}) {
      var _this$config$input$el;
      super($root, config);
      const $input = (_this$config$input$el = this.config.input.element) != null ? _this$config$input$el : this.$root.querySelector(this.config.input.selector);
      if (!$input || !($input instanceof HTMLInputElement)) {
        return this;
      }
      this.$input = $input;
      this.dayLabels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      this.monthLabels = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
      this.currentDate = new Date();
      this.currentDate.setHours(0, 0, 0, 0);
      this.calendarDays = /** @type {DSCalendarDay[]} */[];
      this.excludedDates = /** @type {Date[]} */[];
      this.excludedDays = /** @type {number[]} */[];
      this.buttonClass = 'moj-datepicker__button';
      this.selectedDayButtonClass = 'moj-datepicker__button--selected';
      this.currentDayButtonClass = 'moj-datepicker__button--current';
      this.todayButtonClass = 'moj-datepicker__button--today';
      this.setOptions();
      this.initControls();
    }
    initControls() {
      this.id = `datepicker-${this.$input.id}`;
      this.$dialog = this.createDialog();
      this.createCalendarHeaders();
      const $componentWrapper = document.createElement('div');
      const $inputWrapper = document.createElement('div');
      $componentWrapper.classList.add('moj-datepicker__wrapper');
      $inputWrapper.classList.add('govuk-input__wrapper');
      this.$input.parentElement.insertBefore($componentWrapper, this.$input);
      $componentWrapper.appendChild($inputWrapper);
      $inputWrapper.appendChild(this.$input);
      $inputWrapper.insertAdjacentHTML('beforeend', this.toggleTemplate());
      $componentWrapper.insertAdjacentElement('beforeend', this.$dialog);
      this.$calendarButton = /** @type {HTMLButtonElement} */
      this.$root.querySelector('.moj-js-datepicker-toggle');
      this.$dialogTitle = /** @type {HTMLHeadingElement} */
      this.$dialog.querySelector('.moj-js-datepicker-month-year');
      this.createCalendar();
      this.$prevMonthButton = /** @type {HTMLButtonElement} */
      this.$dialog.querySelector('.moj-js-datepicker-prev-month');
      this.$prevYearButton = /** @type {HTMLButtonElement} */
      this.$dialog.querySelector('.moj-js-datepicker-prev-year');
      this.$nextMonthButton = /** @type {HTMLButtonElement} */
      this.$dialog.querySelector('.moj-js-datepicker-next-month');
      this.$nextYearButton = /** @type {HTMLButtonElement} */
      this.$dialog.querySelector('.moj-js-datepicker-next-year');
      this.$cancelButton = /** @type {HTMLButtonElement} */
      this.$dialog.querySelector('.moj-js-datepicker-cancel');
      this.$okButton = /** @type {HTMLButtonElement} */
      this.$dialog.querySelector('.moj-js-datepicker-ok');

      // add event listeners
      this.$prevMonthButton.addEventListener('click', event => this.focusPreviousMonth(event, false));
      this.$prevYearButton.addEventListener('click', event => this.focusPreviousYear(event, false));
      this.$nextMonthButton.addEventListener('click', event => this.focusNextMonth(event, false));
      this.$nextYearButton.addEventListener('click', event => this.focusNextYear(event, false));
      this.$cancelButton.addEventListener('click', event => {
        event.preventDefault();
        this.closeDialog();
      });
      this.$okButton.addEventListener('click', () => {
        this.selectDate(this.currentDate);
      });
      const $dialogButtons = this.$dialog.querySelectorAll('button:not([disabled="true"])');
      this.$firstButtonInDialog = $dialogButtons[0];
      this.$lastButtonInDialog = $dialogButtons[$dialogButtons.length - 1];
      this.$firstButtonInDialog.addEventListener('keydown', event => this.firstButtonKeydown(event));
      this.$lastButtonInDialog.addEventListener('keydown', event => this.lastButtonKeydown(event));
      this.$calendarButton.addEventListener('click', event => this.toggleDialog(event));
      this.$dialog.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
          this.closeDialog();
          event.preventDefault();
          event.stopPropagation();
        }
      });
      document.body.addEventListener('mouseup', event => this.backgroundClick(event));

      // populates calendar with initial dates, avoids Wave errors about null buttons
      this.updateCalendar();
    }
    createDialog() {
      const titleId = `datepicker-title-${this.$input.id}`;
      const $dialog = document.createElement('div');
      $dialog.id = this.id;
      $dialog.setAttribute('class', 'moj-datepicker__dialog');
      $dialog.setAttribute('role', 'dialog');
      $dialog.setAttribute('aria-modal', 'true');
      $dialog.setAttribute('aria-labelledby', titleId);
      $dialog.innerHTML = this.dialogTemplate(titleId);
      $dialog.hidden = true;
      return $dialog;
    }
    createCalendar() {
      const $tbody = this.$dialog.querySelector('tbody');
      let dayCount = 0;
      for (let i = 0; i < 6; i++) {
        // create row
        const $row = $tbody.insertRow(i);
        for (let j = 0; j < 7; j++) {
          // create cell (day)
          const $cell = document.createElement('td');
          const $dateButton = document.createElement('button');
          $cell.appendChild($dateButton);
          $row.appendChild($cell);
          const calendarDay = new DSCalendarDay($dateButton, dayCount, i, j, this);
          this.calendarDays.push(calendarDay);
          dayCount++;
        }
      }
    }
    toggleTemplate() {
      return `<button class="moj-datepicker__toggle moj-js-datepicker-toggle" type="button" aria-haspopup="dialog" aria-controls="${this.id}" aria-expanded="false">
            <span class="govuk-visually-hidden">Choose date</span>
            <svg width="32" height="24" focusable="false" class="moj-datepicker-icon" aria-hidden="true" role="img" viewBox="0 0 22 22">
              <path
                fill="currentColor"
                fill-rule="evenodd"
                clip-rule="evenodd"
                d="M16.1333 2.93333H5.86668V4.4C5.86668 5.21002 5.21003 5.86667 4.40002 5.86667C3.59 5.86667 2.93335 5.21002 2.93335 4.4V2.93333H2C0.895431 2.93333 0 3.82877 0 4.93334V19.2667C0 20.3712 0.89543 21.2667 2 21.2667H20C21.1046 21.2667 22 20.3712 22 19.2667V4.93333C22 3.82876 21.1046 2.93333 20 2.93333H19.0667V4.4C19.0667 5.21002 18.41 5.86667 17.6 5.86667C16.79 5.86667 16.1333 5.21002 16.1333 4.4V2.93333ZM20.5333 8.06667H1.46665V18.8C1.46665 19.3523 1.91436 19.8 2.46665 19.8H19.5333C20.0856 19.8 20.5333 19.3523 20.5333 18.8V8.06667Z"
              ></path>
              <rect x="3.66669" width="1.46667" height="5.13333" rx="0.733333" fill="currentColor"></rect>
              <rect x="16.8667" width="1.46667" height="5.13333" rx="0.733333" fill="currentColor"></rect>
            </svg>
          </button>`;
    }

    /**
     * HTML template for calendar dialog
     *
     * @param {string} [titleId] - Id attribute for dialog title
     * @returns {string}
     */
    dialogTemplate(titleId) {
      return `<div class="moj-datepicker__dialog-header">
            <div class="moj-datepicker__dialog-navbuttons">
              <button class="moj-datepicker__button moj-js-datepicker-prev-year">
                <span class="govuk-visually-hidden">Previous year</span>
                <svg width="44" height="40" viewBox="0 0 44 40" fill="none" fill="none" focusable="false" aria-hidden="true" role="img">
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M23.1643 20L28.9572 14.2071L27.5429 12.7929L20.3358 20L27.5429 27.2071L28.9572 25.7929L23.1643 20Z" fill="currentColor"/>
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M17.1643 20L22.9572 14.2071L21.5429 12.7929L14.3358 20L21.5429 27.2071L22.9572 25.7929L17.1643 20Z" fill="currentColor"/>
                </svg>
              </button>

              <button class="moj-datepicker__button moj-js-datepicker-prev-month">
                <span class="govuk-visually-hidden">Previous month</span>
                <svg width="44" height="40" viewBox="0 0 44 40" fill="none" focusable="false" aria-hidden="true" role="img">
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M20.5729 20L25.7865 14.2071L24.5137 12.7929L18.0273 20L24.5137 27.2071L25.7865 25.7929L20.5729 20Z" fill="currentColor"/>
                </svg>
              </button>
            </div>

            <h2 id="${titleId}" class="moj-datepicker__dialog-title moj-js-datepicker-month-year" aria-live="polite">June 2020</h2>

            <div class="moj-datepicker__dialog-navbuttons">
              <button class="moj-datepicker__button moj-js-datepicker-next-month">
                <span class="govuk-visually-hidden">Next month</span>
                <svg width="44" height="40" viewBox="0 0 44 40" fill="none"  focusable="false" aria-hidden="true" role="img">
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M23.4271 20L18.2135 14.2071L19.4863 12.7929L25.9727 20L19.4863 27.2071L18.2135 25.7929L23.4271 20Z" fill="currentColor"/>
                </svg>
              </button>

              <button class="moj-datepicker__button moj-js-datepicker-next-year">
                <span class="govuk-visually-hidden">Next year</span>
                <svg width="44" height="40" viewBox="0 0 44 40" fill="none" fill="none" focusable="false" aria-hidden="true" role="img">
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M20.8357 20L15.0428 14.2071L16.4571 12.7929L23.6642 20L16.4571 27.2071L15.0428 25.7929L20.8357 20Z" fill="currentColor"/>
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M26.8357 20L21.0428 14.2071L22.4571 12.7929L29.6642 20L22.4571 27.2071L21.0428 25.7929L26.8357 20Z" fill="currentColor"/>
                </svg>
              </button>
            </div>
          </div>

          <table class="moj-datepicker__calendar moj-js-datepicker-grid" role="grid" aria-labelledby="${titleId}">
            <thead>
              <tr></tr>
            </thead>

            <tbody></tbody>
          </table>

          <div class="govuk-button-group">
            <button type="button" class="govuk-button moj-js-datepicker-ok">Select</button>
            <button type="button" class="govuk-button govuk-button--secondary moj-js-datepicker-cancel">Close</button>
          </div>`;
    }
    createCalendarHeaders() {
      this.dayLabels.forEach(day => {
        const html = `<th scope="col"><span aria-hidden="true">${day.substring(0, 3)}</span><span class="govuk-visually-hidden">${day}</span></th>`;
        const $headerRow = this.$dialog.querySelector('thead > tr');
        $headerRow.insertAdjacentHTML('beforeend', html);
      });
    }

    /**
     * Pads given number with leading zeros
     *
     * @param {number} value - The value to be padded
     * @param {number} length - The length in characters of the output
     * @returns {string}
     */
    leadingZeros(value, length = 2) {
      let ret = value.toString();
      while (ret.length < length) {
        ret = `0${ret}`;
      }
      return ret;
    }
    setOptions() {
      this.setMinAndMaxDatesOnCalendar();
      this.setExcludedDates();
      this.setExcludedDays();
      this.setWeekStartDay();
    }
    setMinAndMaxDatesOnCalendar() {
      if (this.config.minDate) {
        this.minDate = this.formattedDateFromString(this.config.minDate, null);
        if (this.minDate && this.currentDate < this.minDate) {
          this.currentDate = this.minDate;
        }
      }
      if (this.config.maxDate) {
        this.maxDate = this.formattedDateFromString(this.config.maxDate, null);
        if (this.maxDate && this.currentDate > this.maxDate) {
          this.currentDate = this.maxDate;
        }
      }
    }
    setExcludedDates() {
      if (this.config.excludedDates) {
        this.excludedDates = this.config.excludedDates.replace(/\s+/, ' ').split(' ').map(item => {
          return item.includes('-') ? this.parseDateRangeString(item) : [this.formattedDateFromString(item)];
        }).reduce((dates, items) => dates.concat(items)).filter(date => date);
      }
    }

    /**
     * Parses a daterange string into an array of dates
     *
     * @param {string} datestring - A daterange string in the format "dd/mm/yyyy-dd/mm/yyyy"
     */
    parseDateRangeString(datestring) {
      const dates = [];
      const [startDate, endDate] = datestring.split('-').map(d => this.formattedDateFromString(d, null));
      if (startDate && endDate) {
        const date = new Date(startDate.getTime());
        /* eslint-disable no-unmodified-loop-condition */
        while (date <= endDate) {
          dates.push(new Date(date));
          date.setDate(date.getDate() + 1);
        }
        /* eslint-enable no-unmodified-loop-condition */
      }
      return dates;
    }
    setExcludedDays() {
      if (this.config.excludedDays) {
        // lowercase and arrange dayLabels to put indexOf sunday == 0 for comparison
        // with getDay() function
        const weekDays = this.dayLabels.map(item => item.toLowerCase());
        if (this.config.weekStartDay === 'monday') {
          weekDays.unshift(weekDays.pop());
        }
        this.excludedDays = this.config.excludedDays.replace(/\s+/, ' ').toLowerCase().split(' ').map(item => weekDays.indexOf(item)).filter(item => item !== -1);
      }
    }
    setWeekStartDay() {
      const weekStartDayParam = this.config.weekStartDay;
      if (weekStartDayParam && weekStartDayParam.toLowerCase() === 'sunday') {
        this.config.weekStartDay = 'sunday';
        // Rotate dayLabels array to put Sunday as the first item
        this.dayLabels.unshift(this.dayLabels.pop());
      } else {
        this.config.weekStartDay = 'monday';
      }
    }

    /**
     * Determine if a date is selectable
     *
     * @param {Date} date - the date to check
     * @returns {boolean}
     */
    isExcludedDate(date) {
      // This comparison does not work correctly - it will exclude the mindate itself
      // see: https://github.com/ministryofjustice/moj-frontend/issues/923
      if (this.minDate && this.minDate > date) {
        return true;
      }

      // This comparison works as expected - the maxdate will not be excluded
      if (this.maxDate && this.maxDate < date) {
        return true;
      }
      for (const excludedDate of this.excludedDates) {
        if (date.toDateString() === excludedDate.toDateString()) {
          return true;
        }
      }
      if (this.excludedDays.includes(date.getDay())) {
        return true;
      }
      return false;
    }

    /**
     * Get a Date object from a string
     *
     * @param {string} dateString - string in the format d/m/yyyy dd/mm/yyyy
     * @param {Date} fallback - date object to return if formatting fails
     * @returns {Date}
     */
    formattedDateFromString(dateString, fallback = new Date()) {
      let formattedDate = null;
      // Accepts d/m/yyyy and dd/mm/yyyy
      const dateFormatPattern = /(\d{1,2})([-/,. ])(\d{1,2})\2(\d{4})/;
      if (!dateFormatPattern.test(dateString)) return fallback;
      const match = dateFormatPattern.exec(dateString);
      const day = match[1];
      const month = match[3];
      const year = match[4];
      formattedDate = new Date(`${year}-${month}-${day}`);
      if (formattedDate instanceof Date && Number.isFinite(formattedDate.getTime())) {
        return formattedDate;
      }
      return fallback;
    }

    /**
     * Get a formatted date string from a Date object
     *
     * @param {Date} date - date to format to a string
     * @returns {string}
     */
    formattedDateFromDate(date) {
      if (this.config.leadingZeros) {
        return `${this.leadingZeros(date.getDate())}/${this.leadingZeros(date.getMonth() + 1)}/${date.getFullYear()}`;
      }
      return `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
    }

    /**
     * Get a human readable date in the format Monday 2 March 2024
     *
     * @param {Date} date - Date to format
     * @returns {string}
     */
    formattedDateHuman(date) {
      return `${this.dayLabels[(date.getDay() + 6) % 7]} ${date.getDate()} ${this.monthLabels[date.getMonth()]} ${date.getFullYear()}`;
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    backgroundClick(event) {
      if (this.isOpen() && event.target instanceof Node && !this.$dialog.contains(event.target) && !this.$input.contains(event.target) && !this.$calendarButton.contains(event.target)) {
        event.preventDefault();
        this.closeDialog();
      }
    }

    /**
     * @param {KeyboardEvent} event - Keydown event
     */
    firstButtonKeydown(event) {
      if (event.key === 'Tab' && event.shiftKey) {
        this.$lastButtonInDialog.focus();
        event.preventDefault();
      }
    }

    /**
     * @param {KeyboardEvent} event - Keydown event
     */
    lastButtonKeydown(event) {
      if (event.key === 'Tab' && !event.shiftKey) {
        this.$firstButtonInDialog.focus();
        event.preventDefault();
      }
    }

    // render calendar
    updateCalendar() {
      this.$dialogTitle.innerHTML = `${this.monthLabels[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;
      const day = this.currentDate;
      const firstOfMonth = new Date(day.getFullYear(), day.getMonth(), 1);
      let dayOfWeek;
      if (this.config.weekStartDay === 'monday') {
        dayOfWeek = firstOfMonth.getDay() === 0 ? 6 : firstOfMonth.getDay() - 1; // Change logic to make Monday first day of week, i.e. 0
      } else {
        dayOfWeek = firstOfMonth.getDay();
      }
      firstOfMonth.setDate(firstOfMonth.getDate() - dayOfWeek);
      const thisDay = new Date(firstOfMonth);

      // loop through our days
      for (const calendarDay of this.calendarDays) {
        const hidden = thisDay.getMonth() !== day.getMonth();
        const disabled = this.isExcludedDate(thisDay);
        calendarDay.update(thisDay, hidden, disabled);
        thisDay.setDate(thisDay.getDate() + 1);
      }
    }

    /**
     * @param {boolean} [focus] - Focus the day button
     */
    setCurrentDate(focus = true) {
      const {
        currentDate
      } = this;
      this.calendarDays.forEach(calendarDay => {
        calendarDay.$button.classList.add('moj-datepicker__button');
        calendarDay.$button.classList.add('moj-datepicker__calendar-day');
        calendarDay.$button.setAttribute('tabindex', '-1');
        calendarDay.$button.classList.remove(this.selectedDayButtonClass);
        const calendarDayDate = calendarDay.date;
        calendarDayDate.setHours(0, 0, 0, 0);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (calendarDayDate.getTime() === currentDate.getTime() /* && !calendarDay.button.disabled */) {
          if (focus) {
            calendarDay.$button.setAttribute('tabindex', '0');
            calendarDay.$button.focus();
            calendarDay.$button.classList.add(this.selectedDayButtonClass);
          }
        }
        if (this.inputDate && calendarDayDate.getTime() === this.inputDate.getTime()) {
          calendarDay.$button.classList.add(this.currentDayButtonClass);
          calendarDay.$button.setAttribute('aria-current', 'date');
        } else {
          calendarDay.$button.classList.remove(this.currentDayButtonClass);
          calendarDay.$button.removeAttribute('aria-current');
        }
        if (calendarDayDate.getTime() === today.getTime()) {
          calendarDay.$button.classList.add(this.todayButtonClass);
        } else {
          calendarDay.$button.classList.remove(this.todayButtonClass);
        }
      });

      // if no date is tab-able, make the first non-disabled date tab-able
      if (!focus) {
        const enabledDays = this.calendarDays.filter(calendarDay => {
          return window.getComputedStyle(calendarDay.$button).display === 'block' && !calendarDay.$button.disabled;
        });
        enabledDays[0].$button.setAttribute('tabindex', '0');
        this.currentDate = enabledDays[0].date;
      }
    }

    /**
     * @param {Date} date - Date to select
     */
    selectDate(date) {
      if (this.isExcludedDate(date)) {
        return;
      }
      this.$calendarButton.querySelector('span').innerText = `Choose date. Selected date is ${this.formattedDateHuman(date)}`;
      this.$input.value = this.formattedDateFromDate(date);
      const changeEvent = new Event('change', {
        bubbles: true,
        cancelable: true
      });
      this.$input.dispatchEvent(changeEvent);
      this.closeDialog();
    }
    isOpen() {
      return this.$dialog.classList.contains('moj-datepicker__dialog--open');
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    toggleDialog(event) {
      event.preventDefault();
      if (this.isOpen()) {
        this.closeDialog();
      } else {
        this.setMinAndMaxDatesOnCalendar();
        this.openDialog();
      }
    }
    openDialog() {
      this.$dialog.hidden = false;
      this.$dialog.classList.add('moj-datepicker__dialog--open');
      this.$calendarButton.setAttribute('aria-expanded', 'true');

      // position the dialog
      // if input is wider than dialog pin it to the right
      if (this.$input.offsetWidth > this.$dialog.offsetWidth) {
        this.$dialog.style.right = `0px`;
      }
      this.$dialog.style.top = `${this.$input.offsetHeight + 3}px`;

      // get the date from the input element
      this.inputDate = this.formattedDateFromString(this.$input.value);
      this.currentDate = this.inputDate;
      this.currentDate.setHours(0, 0, 0, 0);
      this.updateCalendar();
      this.setCurrentDate();
    }
    closeDialog() {
      this.$dialog.hidden = true;
      this.$dialog.classList.remove('moj-datepicker__dialog--open');
      this.$calendarButton.setAttribute('aria-expanded', 'false');
      this.$calendarButton.focus();
    }

    /**
     * @param {Date} date - Date to go to
     * @param {boolean} [focus] - Focus the day button
     */
    goToDate(date, focus) {
      const current = this.currentDate;
      this.currentDate = date;
      if (current.getMonth() !== this.currentDate.getMonth() || current.getFullYear() !== this.currentDate.getFullYear()) {
        this.updateCalendar();
      }
      this.setCurrentDate(focus);
    }

    // day navigation
    focusNextDay() {
      const date = new Date(this.currentDate);
      date.setDate(date.getDate() + 1);
      this.goToDate(date);
    }
    focusPreviousDay() {
      const date = new Date(this.currentDate);
      date.setDate(date.getDate() - 1);
      this.goToDate(date);
    }

    // week navigation
    focusNextWeek() {
      const date = new Date(this.currentDate);
      date.setDate(date.getDate() + 7);
      this.goToDate(date);
    }
    focusPreviousWeek() {
      const date = new Date(this.currentDate);
      date.setDate(date.getDate() - 7);
      this.goToDate(date);
    }
    focusFirstDayOfWeek() {
      const date = new Date(this.currentDate);
      const firstDayOfWeekIndex = this.config.weekStartDay === 'sunday' ? 0 : 1;
      const dayOfWeek = date.getDay();
      const diff = dayOfWeek >= firstDayOfWeekIndex ? dayOfWeek - firstDayOfWeekIndex : 6 - dayOfWeek;
      date.setDate(date.getDate() - diff);
      date.setHours(0, 0, 0, 0);
      this.goToDate(date);
    }
    focusLastDayOfWeek() {
      const date = new Date(this.currentDate);
      const lastDayOfWeekIndex = this.config.weekStartDay === 'sunday' ? 6 : 0;
      const dayOfWeek = date.getDay();
      const diff = dayOfWeek <= lastDayOfWeekIndex ? lastDayOfWeekIndex - dayOfWeek : 7 - dayOfWeek;
      date.setDate(date.getDate() + diff);
      date.setHours(0, 0, 0, 0);
      this.goToDate(date);
    }

    /**
     * Month navigation
     *
     * @param {KeyboardEvent | MouseEvent} event - Key press or click event
     * @param {boolean} [focus] - Focus the day button
     */
    focusNextMonth(event, focus = true) {
      event.preventDefault();
      const date = new Date(this.currentDate);
      date.setMonth(date.getMonth() + 1, 1);
      this.goToDate(date, focus);
    }

    /**
     * @param {KeyboardEvent | MouseEvent} event - Key press or click event
     * @param {boolean} [focus] - Focus the day button
     */
    focusPreviousMonth(event, focus = true) {
      event.preventDefault();
      const date = new Date(this.currentDate);
      date.setMonth(date.getMonth() - 1, 1);
      this.goToDate(date, focus);
    }

    /**
     * Year navigation
     *
     * @param {KeyboardEvent | MouseEvent} event - Key press or click event
     * @param {boolean} [focus] - Focus the day button
     */
    focusNextYear(event, focus = true) {
      event.preventDefault();
      const date = new Date(this.currentDate);
      date.setFullYear(date.getFullYear() + 1, date.getMonth(), 1);
      this.goToDate(date, focus);
    }

    /**
     * @param {KeyboardEvent | MouseEvent} event - Key press or click event
     * @param {boolean} [focus] - Focus the day button
     */
    focusPreviousYear(event, focus = true) {
      event.preventDefault();
      const date = new Date(this.currentDate);
      date.setFullYear(date.getFullYear() - 1, date.getMonth(), 1);
      this.goToDate(date, focus);
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }
  DatePicker.moduleName = 'moj-date-picker';
  /**
   * Date picker default config
   *
   * @type {DatePickerConfig}
   */
  DatePicker.defaults = Object.freeze({
    leadingZeros: false,
    weekStartDay: 'monday',
    input: {
      selector: '.moj-js-datepicker-input'
    }
  });
  /**
   * Date picker config schema
   *
   * @satisfies {Schema<DatePickerConfig>}
   */
  DatePicker.schema = Object.freeze(/** @type {const} */{
    properties: {
      excludedDates: {
        type: 'string'
      },
      excludedDays: {
        type: 'string'
      },
      leadingZeros: {
        type: 'boolean'
      },
      maxDate: {
        type: 'string'
      },
      minDate: {
        type: 'string'
      },
      weekStartDay: {
        type: 'string'
      },
      input: {
        type: 'object'
      }
    }
  });
  class DSCalendarDay {
    /**
     *
     * @param {HTMLButtonElement} $button
     * @param {number} index
     * @param {number} row
     * @param {number} column
     * @param {DatePicker} picker
     */
    constructor($button, index, row, column, picker) {
      this.index = index;
      this.row = row;
      this.column = column;
      this.$button = $button;
      this.picker = picker;
      this.date = new Date();
      this.$button.addEventListener('keydown', this.keyPress.bind(this));
      this.$button.addEventListener('click', this.click.bind(this));
    }

    /**
     * @param {Date} day - the Date for the calendar day
     * @param {boolean} hidden - visibility of the day
     * @param {boolean} disabled - is the day selectable or excluded
     */
    update(day, hidden, disabled) {
      const label = day.getDate();
      let accessibleLabel = this.picker.formattedDateHuman(day);
      if (disabled) {
        this.$button.setAttribute('aria-disabled', 'true');
        accessibleLabel = `Excluded date, ${accessibleLabel}`;
      } else {
        this.$button.removeAttribute('aria-disabled');
      }
      if (hidden) {
        this.$button.style.display = 'none';
      } else {
        this.$button.style.display = 'block';
      }
      this.$button.setAttribute('data-testid', this.picker.formattedDateFromDate(day));
      this.$button.innerHTML = `<span class="govuk-visually-hidden">${accessibleLabel}</span><span aria-hidden="true">${label}</span>`;
      this.date = new Date(day);
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    click(event) {
      this.picker.goToDate(this.date);
      this.picker.selectDate(this.date);
      event.stopPropagation();
      event.preventDefault();
    }

    /**
     * @param {KeyboardEvent} event - Keydown event
     */
    keyPress(event) {
      let calendarNavKey = true;
      switch (event.key) {
        case 'ArrowLeft':
          this.picker.focusPreviousDay();
          break;
        case 'ArrowRight':
          this.picker.focusNextDay();
          break;
        case 'ArrowUp':
          this.picker.focusPreviousWeek();
          break;
        case 'ArrowDown':
          this.picker.focusNextWeek();
          break;
        case 'Home':
          this.picker.focusFirstDayOfWeek();
          break;
        case 'End':
          this.picker.focusLastDayOfWeek();
          break;
        case 'PageUp':
          {
            if (event.shiftKey) {
              this.picker.focusPreviousYear(event);
            } else {
              this.picker.focusPreviousMonth(event);
            }
            break;
          }
        case 'PageDown':
          {
            if (event.shiftKey) {
              this.picker.focusNextYear(event);
            } else {
              this.picker.focusNextMonth(event);
            }
            break;
          }
        default:
          calendarNavKey = false;
          break;
      }
      if (calendarNavKey) {
        event.preventDefault();
        event.stopPropagation();
      }
    }
  }

  /**
   * Date picker config
   *
   * @typedef {object} DatePickerConfig
   * @property {string} [excludedDates] - Dates that cannot be selected
   * @property {string} [excludedDays] - Days that cannot be selected
   * @property {boolean} [leadingZeros] - Whether to add leading zeroes when populating the field
   * @property {string} [minDate] - The earliest available date
   * @property {string} [maxDate] - The latest available date
   * @property {string} [weekStartDay] - First day of the week in calendar view
   * @property {object} [input] - Input config
   * @property {string} [input.selector] - Selector for the input element
   * @property {Element | null} [input.element] - HTML element for the input
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */

  /**
   * @augments {ConfigurableComponent<FilterToggleButtonConfig>}
   */
  class FilterToggleButton extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for filter toggle button
     * @param {FilterToggleButtonConfig} [config] - Filter toggle button config
     */
    constructor($root, config = {}) {
      var _this$config$toggleBu, _this$config$closeBut;
      super($root, config);
      const $toggleButtonContainer = (_this$config$toggleBu = this.config.toggleButtonContainer.element) != null ? _this$config$toggleBu : document.querySelector(this.config.toggleButtonContainer.selector);
      const $closeButtonContainer = (_this$config$closeBut = this.config.closeButtonContainer.element) != null ? _this$config$closeBut : this.$root.querySelector(this.config.closeButtonContainer.selector);
      if (!($toggleButtonContainer instanceof HTMLElement && $closeButtonContainer instanceof HTMLElement)) {
        return this;
      }
      this.$toggleButtonContainer = $toggleButtonContainer;
      this.$closeButtonContainer = $closeButtonContainer;
      this.createToggleButton();
      this.setupResponsiveChecks();
      this.$root.setAttribute('tabindex', '-1');
      if (this.config.startHidden) {
        this.hideMenu();
      }
    }
    setupResponsiveChecks() {
      this.mq = window.matchMedia(this.config.bigModeMediaQuery);
      this.mq.addListener(this.checkMode.bind(this));
      this.checkMode();
    }
    createToggleButton() {
      this.$menuButton = document.createElement('button');
      this.$menuButton.setAttribute('type', 'button');
      this.$menuButton.setAttribute('aria-haspopup', 'true');
      this.$menuButton.setAttribute('aria-expanded', 'false');
      this.$menuButton.className = `govuk-button ${this.config.toggleButton.classes}`;
      this.$menuButton.textContent = this.config.toggleButton.showText;
      this.$menuButton.addEventListener('click', this.onMenuButtonClick.bind(this));
      this.$toggleButtonContainer.append(this.$menuButton);
    }
    checkMode() {
      if (this.mq.matches) {
        this.enableBigMode();
      } else {
        this.enableSmallMode();
      }
    }
    enableBigMode() {
      this.showMenu();
      this.removeCloseButton();
    }
    enableSmallMode() {
      this.hideMenu();
      this.addCloseButton();
    }
    addCloseButton() {
      this.$closeButton = document.createElement('button');
      this.$closeButton.setAttribute('type', 'button');
      this.$closeButton.className = this.config.closeButton.classes;
      this.$closeButton.textContent = this.config.closeButton.text;
      this.$closeButton.addEventListener('click', this.onCloseClick.bind(this));
      this.$closeButtonContainer.append(this.$closeButton);
    }
    onCloseClick() {
      this.hideMenu();
      this.$menuButton.focus();
    }
    removeCloseButton() {
      if (this.$closeButton) {
        this.$closeButton.remove();
        this.$closeButton = null;
      }
    }
    hideMenu() {
      this.$menuButton.setAttribute('aria-expanded', 'false');
      this.$root.classList.add('moj-js-hidden');
      this.$menuButton.textContent = this.config.toggleButton.showText;
    }
    showMenu() {
      this.$menuButton.setAttribute('aria-expanded', 'true');
      this.$root.classList.remove('moj-js-hidden');
      this.$menuButton.textContent = this.config.toggleButton.hideText;
    }
    onMenuButtonClick() {
      this.toggle();
    }
    toggle() {
      if (this.$menuButton.getAttribute('aria-expanded') === 'false') {
        this.showMenu();
        this.$root.focus();
      } else {
        this.hideMenu();
      }
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }

  /**
   * @typedef {object} FilterToggleButtonConfig
   * @property {string} [bigModeMediaQuery] - Media query for big mode
   * @property {boolean} [startHidden] - Whether to start hidden
   * @property {object} [toggleButton] - Toggle button config
   * @property {string} [toggleButton.showText] - Text for show button
   * @property {string} [toggleButton.hideText] - Text for hide button
   * @property {string} [toggleButton.classes] - Classes for toggle button
   * @property {object} [toggleButtonContainer] - Toggle button container config
   * @property {string} [toggleButtonContainer.selector] - Selector for toggle button container
   * @property {Element | null} [toggleButtonContainer.element] - HTML element for toggle button container
   * @property {object} [closeButton] - Close button config
   * @property {string} [closeButton.text] - Text for close button
   * @property {string} [closeButton.classes] - Classes for close button
   * @property {object} [closeButtonContainer] - Close button container config
   * @property {string} [closeButtonContainer.selector] - Selector for close button container
   * @property {Element | null} [closeButtonContainer.element] - HTML element for close button container
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */
  FilterToggleButton.moduleName = 'moj-filter';
  /**
   * Filter toggle button config
   *
   * @type {FilterToggleButtonConfig}
   */
  FilterToggleButton.defaults = Object.freeze({
    bigModeMediaQuery: '(min-width: 48.0625em)',
    startHidden: true,
    toggleButton: {
      showText: 'Show filter',
      hideText: 'Hide filter',
      classes: 'govuk-button--secondary'
    },
    toggleButtonContainer: {
      selector: '.moj-action-bar__filter'
    },
    closeButton: {
      text: 'Close',
      classes: 'moj-filter__close'
    },
    closeButtonContainer: {
      selector: '.moj-filter__header-action'
    }
  });
  /**
   * Filter toggle button config schema
   *
   * @satisfies {Schema<FilterToggleButtonConfig>}
   */
  FilterToggleButton.schema = Object.freeze(/** @type {const} */{
    properties: {
      bigModeMediaQuery: {
        type: 'string'
      },
      startHidden: {
        type: 'boolean'
      },
      toggleButton: {
        type: 'object'
      },
      toggleButtonContainer: {
        type: 'object'
      },
      closeButton: {
        type: 'object'
      },
      closeButtonContainer: {
        type: 'object'
      }
    }
  });

  /**
   * @augments {ConfigurableComponent<FormValidatorConfig, HTMLFormElement>}
   */
  class FormValidator extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for form validator
     * @param {FormValidatorConfig} [config] - Form validator config
     */
    constructor($root, config = {}) {
      super($root, config);
      const $summary = this.config.summary.element || document.querySelector(this.config.summary.selector);
      if (!$summary || !($summary instanceof HTMLElement)) {
        return this;
      }
      this.$summary = $summary;
      this.errors = /** @type {ValidationError[]} */[];
      this.validators = /** @type {Validator[]} */[];
      this.originalTitle = document.title;
      this.$root.addEventListener('submit', this.onSubmit.bind(this));
    }
    escapeHtml(string = '') {
      return String(string).replace(/[&<>"'`=/]/g, name => FormValidator.entityMap[name]);
    }
    resetTitle() {
      document.title = this.originalTitle;
    }
    updateTitle() {
      document.title = `${this.errors.length} errors - ${document.title}`;
    }
    showSummary() {
      this.$summary.innerHTML = this.getSummaryHtml();
      this.$summary.classList.remove('moj-hidden');
      this.$summary.setAttribute('aria-labelledby', 'errorSummary-heading');
      this.$summary.focus();
    }
    getSummaryHtml() {
      let html = '<h2 id="error-summary-title" class="govuk-error-summary__title">There is a problem</h2>';
      html += '<div class="govuk-error-summary__body">';
      html += '<ul class="govuk-list govuk-error-summary__list">';
      for (const error of this.errors) {
        html += '<li>';
        html += `<a href="#${this.escapeHtml(error.fieldName)}">`;
        html += this.escapeHtml(error.message);
        html += '</a>';
        html += '</li>';
      }
      html += '</ul>';
      html += '</div>';
      return html;
    }
    hideSummary() {
      this.$summary.classList.add('moj-hidden');
      this.$summary.removeAttribute('aria-labelledby');
    }

    /**
     * @param {SubmitEvent} event - Form submit event
     */
    onSubmit(event) {
      this.removeInlineErrors();
      this.hideSummary();
      this.resetTitle();
      if (!this.validate()) {
        event.preventDefault();
        this.updateTitle();
        this.showSummary();
        this.showInlineErrors();
      }
    }
    showInlineErrors() {
      for (const error of this.errors) {
        this.showInlineError(error);
      }
    }

    /**
     * @param {ValidationError} error
     */
    showInlineError(error) {
      const $errorSpan = document.createElement('span');
      $errorSpan.id = `${error.fieldName}-error`;
      $errorSpan.classList.add('govuk-error-message');
      $errorSpan.innerHTML = this.escapeHtml(error.message);
      const $control = document.querySelector(`#${error.fieldName}`);
      const $fieldset = $control.closest('.govuk-fieldset');
      const $fieldContainer = ($fieldset || $control).closest('.govuk-form-group');
      const $label = $fieldContainer.querySelector('label');
      const $legend = $fieldContainer.querySelector('legend');
      $fieldContainer.classList.add('govuk-form-group--error');
      if ($fieldset && $legend) {
        $legend.after($errorSpan);
        $fieldContainer.setAttribute('aria-invalid', 'true');
        addAttributeValue($fieldset, 'aria-describedby', $errorSpan.id);
      } else if ($label && $control) {
        $label.after($errorSpan);
        $control.setAttribute('aria-invalid', 'true');
        addAttributeValue($control, 'aria-describedby', $errorSpan.id);
      }
    }
    removeInlineErrors() {
      for (const error of this.errors) {
        this.removeInlineError(error);
      }
    }

    /**
     * @param {ValidationError} error
     */
    removeInlineError(error) {
      const $errorSpan = document.querySelector(`#${error.fieldName}-error`);
      const $control = document.querySelector(`#${error.fieldName}`);
      const $fieldset = $control.closest('.govuk-fieldset');
      const $fieldContainer = ($fieldset || $control).closest('.govuk-form-group');
      const $label = $fieldContainer.querySelector('label');
      const $legend = $fieldContainer.querySelector('legend');
      $errorSpan.remove();
      $fieldContainer.classList.remove('govuk-form-group--error');
      if ($fieldset && $legend) {
        $fieldContainer.removeAttribute('aria-invalid');
        removeAttributeValue($fieldset, 'aria-describedby', $errorSpan.id);
      } else if ($label && $control) {
        $control.removeAttribute('aria-invalid');
        removeAttributeValue($control, 'aria-describedby', $errorSpan.id);
      }
    }

    /**
     * @param {string} fieldName - Field name
     * @param {ValidationRule[]} rules - Validation rules
     */
    addValidator(fieldName, rules) {
      this.validators.push({
        fieldName,
        rules,
        field: this.$root.elements.namedItem(fieldName)
      });
    }
    validate() {
      this.errors = [];

      /** @type {Validator | null} */
      let validator = null;

      /** @type {boolean | string} */
      let validatorReturnValue = true;
      let i;
      let j;
      for (i = 0; i < this.validators.length; i++) {
        validator = this.validators[i];
        for (j = 0; j < validator.rules.length; j++) {
          validatorReturnValue = validator.rules[j].method(validator.field, validator.rules[j].params);
          if (typeof validatorReturnValue === 'boolean' && !validatorReturnValue) {
            this.errors.push({
              fieldName: validator.fieldName,
              message: validator.rules[j].message
            });
            break;
          } else if (typeof validatorReturnValue === 'string') {
            this.errors.push({
              fieldName: validatorReturnValue,
              message: validator.rules[j].message
            });
            break;
          }
        }
      }
      return this.errors.length === 0;
    }

    /**
     * @type {Record<string, string>}
     */
  }

  /**
   * @typedef {object} FormValidatorConfig
   * @property {object} [summary] - Error summary config
   * @property {string} [summary.selector] - Selector for error summary
   * @property {Element | null} [summary.element] - HTML element for error summary
   */

  /**
   * @typedef {object} ValidationRule
   * @property {(field: Validator['field'], params: Record<string, Validator['field']>) => boolean | string} method - Validation method
   * @property {string} message - Error message
   * @property {Record<string, Validator['field']>} [params] - Parameters for validation
   */

  /**
   * @typedef {object} ValidationError
   * @property {string} fieldName - Name of the field
   * @property {string} message - Validation error message
   */

  /**
   * @typedef {object} Validator
   * @property {string} fieldName - Name of the field
   * @property {ValidationRule[]} rules - Validation rules
   * @property {Element | RadioNodeList} field - Form field
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */
  FormValidator.entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
    '/': '&#x2F;',
    '`': '&#x60;',
    '=': '&#x3D;'
  };
  /**
   * Name for the component used when initialising using data-module attributes.
   */
  FormValidator.moduleName = 'moj-form-validator';
  /**
   * Multi file upload default config
   *
   * @type {FormValidatorConfig}
   */
  FormValidator.defaults = Object.freeze({
    summary: {
      selector: '.govuk-error-summary'
    }
  });
  /**
   * Multi file upload config schema
   *
   * @satisfies {Schema<FormValidatorConfig>}
   */
  FormValidator.schema = Object.freeze(/** @type {const} */{
    properties: {
      summary: {
        type: 'object'
      }
    }
  });

  /* eslint-disable @typescript-eslint/no-empty-function */


  /**
   * @augments {ConfigurableComponent<MultiFileUploadConfig>}
   */
  class MultiFileUpload extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for multi file upload
     * @param {MultiFileUploadConfig} [config] - Multi file upload config
     */
    constructor($root, config = {}) {
      var _this$config$feedback;
      super($root, config);
      if (!MultiFileUpload.isSupported()) {
        return this;
      }
      const $feedbackContainer = (_this$config$feedback = this.config.feedbackContainer.element) != null ? _this$config$feedback : this.$root.querySelector(this.config.feedbackContainer.selector);
      if (!$feedbackContainer || !($feedbackContainer instanceof HTMLElement)) {
        return this;
      }
      this.$feedbackContainer = $feedbackContainer;
      this.setupFileInput();
      this.setupDropzone();
      this.setupLabel();
      this.setupStatusBox();
      this.$root.addEventListener('click', this.onFileDeleteClick.bind(this));
      this.$root.classList.add('moj-multi-file-upload--enhanced');
    }
    setupDropzone() {
      this.$dropzone = document.createElement('div');
      this.$dropzone.classList.add('moj-multi-file-upload__dropzone');
      this.$dropzone.addEventListener('dragover', this.onDragOver.bind(this));
      this.$dropzone.addEventListener('dragleave', this.onDragLeave.bind(this));
      this.$dropzone.addEventListener('drop', this.onDrop.bind(this));
      this.$fileInput.replaceWith(this.$dropzone);
      this.$dropzone.appendChild(this.$fileInput);
    }
    setupLabel() {
      const $label = document.createElement('label');
      $label.setAttribute('for', this.$fileInput.id);
      $label.classList.add('govuk-button', 'govuk-button--secondary');
      $label.textContent = this.config.dropzoneButtonText;
      const $hint = document.createElement('p');
      $hint.classList.add('govuk-body');
      $hint.textContent = this.config.dropzoneHintText;
      this.$label = $label;
      this.$dropzone.append($hint);
      this.$dropzone.append($label);
    }
    setupFileInput() {
      this.$fileInput = /** @type {HTMLInputElement} */
      this.$root.querySelector('.moj-multi-file-upload__input');
      this.$fileInput.addEventListener('change', this.onFileChange.bind(this));
      this.$fileInput.addEventListener('focus', this.onFileFocus.bind(this));
      this.$fileInput.addEventListener('blur', this.onFileBlur.bind(this));
    }
    setupStatusBox() {
      this.$status = document.createElement('div');
      this.$status.classList.add('govuk-visually-hidden');
      this.$status.setAttribute('aria-live', 'polite');
      this.$status.setAttribute('role', 'status');
      this.$dropzone.append(this.$status);
    }

    /**
     * @param {DragEvent} event - Drag event
     */
    onDragOver(event) {
      event.preventDefault();
      this.$dropzone.classList.add('moj-multi-file-upload--dragover');
    }
    onDragLeave() {
      this.$dropzone.classList.remove('moj-multi-file-upload--dragover');
    }

    /**
     * @param {DragEvent} event - Drag event
     */
    onDrop(event) {
      event.preventDefault();
      this.$dropzone.classList.remove('moj-multi-file-upload--dragover');
      this.$feedbackContainer.classList.remove('moj-hidden');
      this.$status.textContent = this.config.uploadStatusText;
      this.uploadFiles(event.dataTransfer.files);
    }

    /**
     * @param {FileList} files - File list
     */
    uploadFiles(files) {
      for (const file of Array.from(files)) {
        this.uploadFile(file);
      }
    }
    onFileChange() {
      this.$feedbackContainer.classList.remove('moj-hidden');
      this.$status.textContent = this.config.uploadStatusText;
      this.uploadFiles(this.$fileInput.files);
      const $fileInput = this.$fileInput.cloneNode(true);
      if (!$fileInput || !($fileInput instanceof HTMLInputElement)) {
        return;
      }
      $fileInput.value = '';
      this.$fileInput.replaceWith($fileInput);
      this.setupFileInput();
      this.$fileInput.focus();
    }
    onFileFocus() {
      this.$label.classList.add('moj-multi-file-upload--focused');
    }
    onFileBlur() {
      this.$label.classList.remove('moj-multi-file-upload--focused');
    }

    /**
     * @param {UploadResponseSuccess['success']} success
     */
    getSuccessHtml(success) {
      return `<span class="moj-multi-file-upload__success"> <svg class="moj-banner__icon" fill="currentColor" role="presentation" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 25" height="25" width="25"><path d="M25,6.2L8.7,23.2L0,14.1l4-4.2l4.7,4.9L21,2L25,6.2z"/></svg>${success.messageHtml}</span>`;
    }

    /**
     * @param {UploadResponseError['error']} error
     */
    getErrorHtml(error) {
      return `<span class="moj-multi-file-upload__error"> <svg class="moj-banner__icon" fill="currentColor" role="presentation" focusable="false" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 25" height="25" width="25"><path d="M13.6,15.4h-2.3v-4.5h2.3V15.4z M13.6,19.8h-2.3v-2.2h2.3V19.8z M0,23.2h25L12.5,2L0,23.2z"/></svg>${error.message}</span>`;
    }

    /**
     * @param {File} file
     */
    getFileRow(file) {
      const $row = document.createElement('div');
      $row.classList.add('govuk-summary-list__row', 'moj-multi-file-upload__row');
      $row.innerHTML = `
    <div class="govuk-summary-list__value moj-multi-file-upload__message">
      <span class="moj-multi-file-upload__filename">${file.name}</span>
      <span class="moj-multi-file-upload__progress">0%</span>
    </div>
    <div class="govuk-summary-list__actions moj-multi-file-upload__actions"></div>
  `;
      return $row;
    }

    /**
     * @param {UploadResponseFile} file
     */
    getDeleteButton(file) {
      const $button = document.createElement('button');
      $button.setAttribute('type', 'button');
      $button.setAttribute('name', 'delete');
      $button.setAttribute('value', file.filename);
      $button.classList.add('moj-multi-file-upload__delete', 'govuk-button', 'govuk-button--secondary', 'govuk-!-margin-bottom-0');
      $button.innerHTML = `Delete <span class="govuk-visually-hidden">${file.originalname}</span>`;
      return $button;
    }

    /**
     * @param {File} file
     */
    uploadFile(file) {
      this.config.hooks.entryHook(this, file);
      const $item = this.getFileRow(file);
      const $message = $item.querySelector('.moj-multi-file-upload__message');
      const $actions = $item.querySelector('.moj-multi-file-upload__actions');
      const $progress = $item.querySelector('.moj-multi-file-upload__progress');
      const formData = new FormData();
      formData.append('documents', file);
      this.$feedbackContainer.querySelector('.moj-multi-file-upload__list').append($item);
      const xhr = new XMLHttpRequest();
      const onLoad = () => {
        if (xhr.status < 200 || xhr.status >= 300 || !('success' in xhr.response)) {
          return onError();
        }
        $message.innerHTML = this.getSuccessHtml(xhr.response.success);
        this.$status.textContent = xhr.response.success.messageText;
        $actions.append(this.getDeleteButton(xhr.response.file));
        this.config.hooks.exitHook(this, file, xhr, xhr.responseText);
      };
      const onError = () => {
        const error = new Error(xhr.response && 'error' in xhr.response ? xhr.response.error.message : xhr.statusText || 'Upload failed');
        $message.innerHTML = this.getErrorHtml(error);
        this.$status.textContent = error.message;
        this.config.hooks.errorHook(this, file, xhr, xhr.responseText, error);
      };
      xhr.addEventListener('load', onLoad);
      xhr.addEventListener('error', onError);
      xhr.upload.addEventListener('progress', event => {
        if (!event.lengthComputable) {
          return;
        }
        const percentComplete = Math.round(event.loaded / event.total * 100);
        $progress.textContent = ` ${percentComplete}%`;
      });
      xhr.open('POST', this.config.uploadUrl);
      xhr.responseType = 'json';
      xhr.send(formData);
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    onFileDeleteClick(event) {
      const $button = event.target;
      if (!$button || !($button instanceof HTMLButtonElement) || !$button.classList.contains('moj-multi-file-upload__delete')) {
        return;
      }
      event.preventDefault(); // if user refreshes page and then deletes

      const xhr = new XMLHttpRequest();
      xhr.addEventListener('load', () => {
        if (xhr.status < 200 || xhr.status >= 300) {
          return;
        }
        const $rows = Array.from(this.$feedbackContainer.querySelectorAll('.moj-multi-file-upload__row'));
        if ($rows.length === 1) {
          this.$feedbackContainer.classList.add('moj-hidden');
        }
        const $rowDelete = $rows.find($row => $row.contains($button));
        if ($rowDelete) $rowDelete.remove();
        this.config.hooks.deleteHook(this, undefined, xhr, xhr.responseText);
      });
      xhr.open('POST', this.config.deleteUrl);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.responseType = 'json';
      xhr.send(JSON.stringify({
        [$button.name]: $button.value
      }));
    }
    static isSupported() {
      return this.isDragAndDropSupported() && this.isFormDataSupported() && this.isFileApiSupported();
    }
    static isDragAndDropSupported() {
      const div = document.createElement('div');
      return typeof div.ondrop !== 'undefined';
    }
    static isFormDataSupported() {
      return typeof FormData === 'function';
    }
    static isFileApiSupported() {
      const input = document.createElement('input');
      input.type = 'file';
      return typeof input.files !== 'undefined';
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }

  /**
   * Multi file upload config
   *
   * @typedef {object} MultiFileUploadConfig
   * @property {string} [uploadUrl] - File upload URL
   * @property {string} [deleteUrl] - File delete URL
   * @property {string} [uploadStatusText] - Upload status text
   * @property {string} [dropzoneHintText] - Dropzone hint text
   * @property {string} [dropzoneButtonText] - Dropzone button text
   * @property {object} [feedbackContainer] - Feedback container config
   * @property {string} [feedbackContainer.selector] - Selector for feedback container
   * @property {Element | null} [feedbackContainer.element] - HTML element for feedback container
   * @property {MultiFileUploadHooks} [hooks] - Upload hooks
   */

  /**
   * Multi file upload hooks
   *
   * @typedef {object} MultiFileUploadHooks
   * @property {OnUploadFileEntryHook} [entryHook] - File upload entry hook
   * @property {OnUploadFileExitHook} [exitHook] - File upload exit hook
   * @property {OnUploadFileErrorHook} [errorHook] - File upload error hook
   * @property {OnUploadFileDeleteHook} [deleteHook] - File delete hook
   */

  /**
   * Upload hook: File entry
   *
   * @callback OnUploadFileEntryHook
   * @param {InstanceType<typeof MultiFileUpload>} upload - Multi file upload
   * @param {File} file - File upload
   */

  /**
   * Upload hook: File exit
   *
   * @callback OnUploadFileExitHook
   * @param {InstanceType<typeof MultiFileUpload>} upload - Multi file upload
   * @param {File} file - File upload
   * @param {XMLHttpRequest} xhr - XMLHttpRequest
   * @param {string} textStatus - Text status
   */

  /**
   * Upload hook: File error
   *
   * @callback OnUploadFileErrorHook
   * @param {InstanceType<typeof MultiFileUpload>} upload - Multi file upload
   * @param {File} file - File upload
   * @param {XMLHttpRequest} xhr - XMLHttpRequest
   * @param {string} textStatus - Text status
   * @param {Error} errorThrown - Error thrown
   */

  /**
   * Upload hook: File delete
   *
   * @callback OnUploadFileDeleteHook
   * @param {InstanceType<typeof MultiFileUpload>} upload - Multi file upload
   * @param {File} [file] - File upload
   * @param {XMLHttpRequest} xhr - XMLHttpRequest
   * @param {string} textStatus - Text status
   */

  /**
   * @typedef {object} UploadResponseSuccess
   * @property {{ messageText: string, messageHtml: string }} success - Response success
   * @property {UploadResponseFile} file - Response file
   */

  /**
   * @typedef {object} UploadResponseError
   * @property {{ message: string }} error - Response error
   * @property {UploadResponseFile} file - Response file
   */

  /**
   * @typedef {object} UploadResponseFile
   * @property {string} filename - File name
   * @property {string} originalname - Original file name
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */
  MultiFileUpload.moduleName = 'moj-multi-file-upload';
  /**
   * Multi file upload default config
   *
   * @type {MultiFileUploadConfig}
   */
  MultiFileUpload.defaults = Object.freeze({
    uploadStatusText: 'Uploading files, please wait',
    dropzoneHintText: 'Drag and drop files here or',
    dropzoneButtonText: 'Choose files',
    feedbackContainer: {
      selector: '.moj-multi-file__uploaded-files'
    },
    hooks: {
      entryHook: () => {},
      exitHook: () => {},
      errorHook: () => {},
      deleteHook: () => {}
    }
  });
  /**
   * Multi file upload config schema
   *
   * @satisfies {Schema<MultiFileUploadConfig>}
   */
  MultiFileUpload.schema = Object.freeze(/** @type {const} */{
    properties: {
      uploadUrl: {
        type: 'string'
      },
      deleteUrl: {
        type: 'string'
      },
      uploadStatusText: {
        type: 'string'
      },
      dropzoneHintText: {
        type: 'string'
      },
      dropzoneButtonText: {
        type: 'string'
      },
      feedbackContainer: {
        type: 'object'
      },
      hooks: {
        type: 'object'
      }
    }
  });

  /**
   * @augments {ConfigurableComponent<MultiSelectConfig>}
   */
  class MultiSelect extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for multi select
     * @param {MultiSelectConfig} [config] - Multi select config
     */
    constructor($root, config = {}) {
      var _this$config$checkbox;
      super($root, config);
      const $container = this.$root.querySelector(`#${this.config.idPrefix}select-all`);
      const $checkboxes = /** @type {NodeListOf<HTMLInputElement>} */(_this$config$checkbox = this.config.checkboxes.items) != null ? _this$config$checkbox : this.$root.querySelectorAll(this.config.checkboxes.selector);
      if (!$container || !($container instanceof HTMLElement) || !$checkboxes.length) {
        return this;
      }
      this.setupToggle(this.config.idPrefix);
      this.$toggleButton = this.$toggle.querySelector('input');
      this.$toggleButton.addEventListener('click', this.onButtonClick.bind(this));
      this.$container = $container;
      this.$container.append(this.$toggle);
      this.$checkboxes = Array.from($checkboxes);
      this.$checkboxes.forEach($input => $input.addEventListener('click', this.onCheckboxClick.bind(this)));
      this.checked = config.checked || false;
    }
    setupToggle(idPrefix = '') {
      const id = `${idPrefix}checkboxes-all`;
      const $toggle = document.createElement('div');
      const $label = document.createElement('label');
      const $input = document.createElement('input');
      const $span = document.createElement('span');
      $toggle.classList.add('govuk-checkboxes__item', 'govuk-checkboxes--small', 'moj-multi-select__checkbox');
      $input.id = id;
      $input.type = 'checkbox';
      $input.classList.add('govuk-checkboxes__input');
      $label.setAttribute('for', id);
      $label.classList.add('govuk-label', 'govuk-checkboxes__label', 'moj-multi-select__toggle-label');
      $span.classList.add('govuk-visually-hidden');
      $span.textContent = 'Select all';
      $label.append($span);
      $toggle.append($input, $label);
      this.$toggle = $toggle;
    }
    onButtonClick() {
      if (this.checked) {
        this.uncheckAll();
        this.$toggleButton.checked = false;
      } else {
        this.checkAll();
        this.$toggleButton.checked = true;
      }
    }
    checkAll() {
      this.$checkboxes.forEach($input => {
        $input.checked = true;
      });
      this.checked = true;
    }
    uncheckAll() {
      this.$checkboxes.forEach($input => {
        $input.checked = false;
      });
      this.checked = false;
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    onCheckboxClick(event) {
      if (!(event.target instanceof HTMLInputElement)) {
        return;
      }
      if (!event.target.checked) {
        this.$toggleButton.checked = false;
        this.checked = false;
      } else {
        if (this.$checkboxes.filter($input => $input.checked).length === this.$checkboxes.length) {
          this.$toggleButton.checked = true;
          this.checked = true;
        }
      }
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }

  /**
   * Multi select config
   *
   * @typedef {object} MultiSelectConfig
   * @property {string} [idPrefix] - Prefix for the Select all" checkbox `id` attribute
   * @property {boolean} [checked] - Whether the "Select all" checkbox is checked
   * @property {object} [checkboxes] - Checkboxes config
   * @property {string} [checkboxes.selector] - Checkboxes query selector
   * @property {NodeListOf<HTMLInputElement>} [checkboxes.items] - Checkboxes query selector results
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */
  MultiSelect.moduleName = 'moj-multi-select';
  /**
   * Multi select config
   *
   * @type {MultiSelectConfig}
   */
  MultiSelect.defaults = Object.freeze({
    idPrefix: '',
    checkboxes: {
      selector: 'tbody input.govuk-checkboxes__input'
    }
  });
  /**
   * Multi select config schema
   *
   * @satisfies {Schema<MultiSelectConfig>}
   */
  MultiSelect.schema = Object.freeze(/** @type {const} */{
    properties: {
      idPrefix: {
        type: 'string'
      },
      checked: {
        type: 'boolean'
      },
      checkboxes: {
        type: 'object'
      }
    }
  });

  class PasswordReveal extends govukFrontend.Component {
    /**
     * @param {Element | null} $root - HTML element to use for password reveal
     */
    constructor($root) {
      super($root);
      const $input = this.$root.querySelector('.govuk-input');
      if (!$input || !($input instanceof HTMLInputElement)) {
        return this;
      }
      this.$input = $input;
      this.$input.setAttribute('spellcheck', 'false');
      this.createButton();
    }
    createButton() {
      this.$group = document.createElement('div');
      this.$button = document.createElement('button');
      this.$button.setAttribute('type', 'button');
      this.$root.classList.add('moj-password-reveal');
      this.$group.classList.add('moj-password-reveal__wrapper');
      this.$button.classList.add('govuk-button', 'govuk-button--secondary', 'moj-password-reveal__button');
      this.$button.innerHTML = 'Show <span class="govuk-visually-hidden">password</span>';
      this.$button.addEventListener('click', this.onButtonClick.bind(this));
      this.$group.append(this.$input, this.$button);
      this.$root.append(this.$group);
    }
    onButtonClick() {
      if (this.$input.type === 'password') {
        this.$input.type = 'text';
        this.$button.innerHTML = 'Hide <span class="govuk-visually-hidden">password</span>';
      } else {
        this.$input.type = 'password';
        this.$button.innerHTML = 'Show <span class="govuk-visually-hidden">password</span>';
      }
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }
  PasswordReveal.moduleName = 'moj-password-reveal';

  /**
   * @augments {ConfigurableComponent<RichTextEditorConfig>}
   */
  class RichTextEditor extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for rich text editor
     * @param {RichTextEditorConfig} config
     */
    constructor($root, config = {}) {
      super($root, config);
      if (!RichTextEditor.isSupported()) {
        return this;
      }
      const $textarea = this.$root.querySelector('.govuk-textarea');
      if (!$textarea || !($textarea instanceof HTMLTextAreaElement)) {
        return this;
      }
      this.$textarea = $textarea;
      this.createToolbar();
      this.hideDefault();
      this.configureToolbar();
      this.keys = {
        left: 37,
        right: 39,
        up: 38,
        down: 40
      };
      this.$content.addEventListener('input', this.onEditorInput.bind(this));
      this.$root.querySelector('label').addEventListener('click', this.onLabelClick.bind(this));
      this.$toolbar.addEventListener('keydown', this.onToolbarKeydown.bind(this));
    }

    /**
     * @param {KeyboardEvent} event - Click event
     */
    onToolbarKeydown(event) {
      let $focusableButton;
      switch (event.keyCode) {
        case this.keys.right:
        case this.keys.down:
          {
            $focusableButton = this.$buttons.find(button => button.getAttribute('tabindex') === '0');
            if ($focusableButton) {
              const $nextButton = $focusableButton.nextElementSibling;
              if ($nextButton && $nextButton instanceof HTMLButtonElement) {
                $nextButton.focus();
                $focusableButton.setAttribute('tabindex', '-1');
                $nextButton.setAttribute('tabindex', '0');
              }
            }
            break;
          }
        case this.keys.left:
        case this.keys.up:
          {
            $focusableButton = this.$buttons.find(button => button.getAttribute('tabindex') === '0');
            if ($focusableButton) {
              const $previousButton = $focusableButton.previousElementSibling;
              if ($previousButton && $previousButton instanceof HTMLButtonElement) {
                $previousButton.focus();
                $focusableButton.setAttribute('tabindex', '-1');
                $previousButton.setAttribute('tabindex', '0');
              }
            }
            break;
          }
      }
    }
    getToolbarHtml() {
      let html = '';
      html += '<div class="moj-rich-text-editor__toolbar" role="toolbar">';
      if (this.config.toolbar.bold) {
        html += '<button class="moj-rich-text-editor__toolbar-button moj-rich-text-editor__toolbar-button--bold" type="button" data-command="bold"><span class="govuk-visually-hidden">Bold</span></button>';
      }
      if (this.config.toolbar.italic) {
        html += '<button class="moj-rich-text-editor__toolbar-button moj-rich-text-editor__toolbar-button--italic" type="button" data-command="italic"><span class="govuk-visually-hidden">Italic</span></button>';
      }
      if (this.config.toolbar.underline) {
        html += '<button class="moj-rich-text-editor__toolbar-button moj-rich-text-editor__toolbar-button--underline" type="button" data-command="underline"><span class="govuk-visually-hidden">Underline</span></button>';
      }
      if (this.config.toolbar.bullets) {
        html += '<button class="moj-rich-text-editor__toolbar-button moj-rich-text-editor__toolbar-button--unordered-list" type="button" data-command="insertUnorderedList"><span class="govuk-visually-hidden">Unordered list</span></button>';
      }
      if (this.config.toolbar.numbers) {
        html += '<button class="moj-rich-text-editor__toolbar-button moj-rich-text-editor__toolbar-button--ordered-list" type="button" data-command="insertOrderedList"><span class="govuk-visually-hidden">Ordered list</span></button>';
      }
      html += '</div>';
      return html;
    }
    getEnhancedHtml() {
      return `${this.getToolbarHtml()}<div class="govuk-textarea moj-rich-text-editor__content" contenteditable="true" spellcheck="false"></div>`;
    }
    hideDefault() {
      this.$textarea.classList.add('govuk-visually-hidden');
      this.$textarea.setAttribute('aria-hidden', 'true');
      this.$textarea.setAttribute('tabindex', '-1');
    }
    createToolbar() {
      this.$toolbar = document.createElement('div');
      this.$toolbar.className = 'moj-rich-text-editor';
      this.$toolbar.innerHTML = this.getEnhancedHtml();
      this.$root.append(this.$toolbar);
      this.$content = /** @type {HTMLElement} */
      this.$root.querySelector('.moj-rich-text-editor__content');
      this.$content.innerHTML = this.$textarea.value;
    }
    configureToolbar() {
      this.$buttons = Array.from(/** @type {NodeListOf<HTMLButtonElement>} */
      this.$root.querySelectorAll('.moj-rich-text-editor__toolbar-button'));
      this.$buttons.forEach(($button, index) => {
        $button.setAttribute('tabindex', !index ? '0' : '-1');
        $button.addEventListener('click', this.onButtonClick.bind(this));
      });
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    onButtonClick(event) {
      if (!(event.currentTarget instanceof HTMLElement)) {
        return;
      }
      document.execCommand(event.currentTarget.getAttribute('data-command'), false, undefined);
    }
    getContent() {
      return this.$content.innerHTML;
    }
    onEditorInput() {
      this.updateTextarea();
    }
    updateTextarea() {
      document.execCommand('defaultParagraphSeparator', false, 'p');
      this.$textarea.value = this.getContent();
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    onLabelClick(event) {
      event.preventDefault();
      this.$content.focus();
    }
    static isSupported() {
      return 'contentEditable' in document.documentElement;
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }

  /**
   * Rich text editor config
   *
   * @typedef {object} RichTextEditorConfig
   * @property {RichTextEditorToolbar} [toolbar] - Toolbar options
   */

  /**
   * Rich text editor toolbar options
   *
   * @typedef {object} RichTextEditorToolbar
   * @property {boolean} [bold] - Show the bold button
   * @property {boolean} [italic] - Show the italic button
   * @property {boolean} [underline] - Show the underline button
   * @property {boolean} [bullets] - Show the bullets button
   * @property {boolean} [numbers] - Show the numbers button
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */
  RichTextEditor.moduleName = 'moj-rich-text-editor';
  /**
   * Rich text editor config
   *
   * @type {RichTextEditorConfig}
   */
  RichTextEditor.defaults = Object.freeze({
    toolbar: {
      bold: false,
      italic: false,
      underline: false,
      bullets: true,
      numbers: true
    }
  });
  /**
   * Rich text editor config schema
   *
   * @satisfies {Schema<RichTextEditorConfig>}
   */
  RichTextEditor.schema = Object.freeze(/** @type {const} */{
    properties: {
      toolbar: {
        type: 'object'
      }
    }
  });

  /**
   * @augments {ConfigurableComponent<SearchToggleConfig>}
   */
  class SearchToggle extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for search toggle
     * @param {SearchToggleConfig} [config] - Search toggle config
     */
    constructor($root, config = {}) {
      var _this$config$searchCo, _this$config$toggleBu;
      super($root, config);
      const $searchContainer = (_this$config$searchCo = this.config.searchContainer.element) != null ? _this$config$searchCo : this.$root.querySelector(this.config.searchContainer.selector);
      const $toggleButtonContainer = (_this$config$toggleBu = this.config.toggleButtonContainer.element) != null ? _this$config$toggleBu : this.$root.querySelector(this.config.toggleButtonContainer.selector);
      if (!$searchContainer || !$toggleButtonContainer || !($searchContainer instanceof HTMLElement) || !($toggleButtonContainer instanceof HTMLElement)) {
        return this;
      }
      this.$searchContainer = $searchContainer;
      this.$toggleButtonContainer = $toggleButtonContainer;
      const svg = '<svg viewBox="0 0 20 20" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" class="moj-search-toggle__button__icon"><path d="M7.433,12.5790048 C6.06762625,12.5808611 4.75763941,12.0392925 3.79217348,11.0738265 C2.82670755,10.1083606 2.28513891,8.79837375 2.28699522,7.433 C2.28513891,6.06762625 2.82670755,4.75763941 3.79217348,3.79217348 C4.75763941,2.82670755 6.06762625,2.28513891 7.433,2.28699522 C8.79837375,2.28513891 10.1083606,2.82670755 11.0738265,3.79217348 C12.0392925,4.75763941 12.5808611,6.06762625 12.5790048,7.433 C12.5808611,8.79837375 12.0392925,10.1083606 11.0738265,11.0738265 C10.1083606,12.0392925 8.79837375,12.5808611 7.433,12.5790048 L7.433,12.5790048 Z M14.293,12.579 L13.391,12.579 L13.071,12.269 C14.2300759,10.9245158 14.8671539,9.20813198 14.866,7.433 C14.866,3.32786745 11.5381325,-1.65045755e-15 7.433,-1.65045755e-15 C3.32786745,-1.65045755e-15 -1.65045755e-15,3.32786745 -1.65045755e-15,7.433 C-1.65045755e-15,11.5381325 3.32786745,14.866 7.433,14.866 C9.208604,14.8671159 10.9253982,14.2296624 12.27,13.07 L12.579,13.39 L12.579,14.294 L18.296,20 L20,18.296 L14.294,12.579 L14.293,12.579 Z"></path></svg>';
      this.$toggleButton = document.createElement('button');
      this.$toggleButton.setAttribute('class', 'moj-search-toggle__button');
      this.$toggleButton.setAttribute('type', 'button');
      this.$toggleButton.setAttribute('aria-haspopup', 'true');
      this.$toggleButton.setAttribute('aria-expanded', 'false');
      this.$toggleButton.innerHTML = `${this.config.toggleButton.text} ${svg}`;
      this.$toggleButton.addEventListener('click', this.onToggleButtonClick.bind(this));
      this.$toggleButtonContainer.append(this.$toggleButton);
      document.addEventListener('click', this.onDocumentClick.bind(this));
      document.addEventListener('focusin', this.onDocumentClick.bind(this));
    }
    showMenu() {
      this.$toggleButton.setAttribute('aria-expanded', 'true');
      this.$searchContainer.classList.remove('moj-js-hidden');
      this.$searchContainer.querySelector('input').focus();
    }
    hideMenu() {
      this.$searchContainer.classList.add('moj-js-hidden');
      this.$toggleButton.setAttribute('aria-expanded', 'false');
    }
    onToggleButtonClick() {
      if (this.$toggleButton.getAttribute('aria-expanded') === 'false') {
        this.showMenu();
      } else {
        this.hideMenu();
      }
    }

    /**
     * @param {MouseEvent | FocusEvent} event
     */
    onDocumentClick(event) {
      if (event.target instanceof Node && !this.$toggleButtonContainer.contains(event.target) && !this.$searchContainer.contains(event.target)) {
        this.hideMenu();
      }
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }

  /**
   * @typedef {object} SearchToggleConfig
   * @property {object} [searchContainer] - Search config
   * @property {string} [searchContainer.selector] - Selector for search container
   * @property {Element | null} [searchContainer.element] - HTML element for search container
   * @property {object} [toggleButton] - Toggle button config
   * @property {string} [toggleButton.text] - Text for toggle button
   * @property {object} [toggleButtonContainer] - Toggle button container config
   * @property {string} [toggleButtonContainer.selector] - Selector for toggle button container
   * @property {Element | null} [toggleButtonContainer.element] - HTML element for toggle button container
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */
  SearchToggle.moduleName = 'moj-search-toggle';
  /**
   * Search toggle config
   *
   * @type {SearchToggleConfig}
   */
  SearchToggle.defaults = Object.freeze({
    searchContainer: {
      selector: '.moj-search'
    },
    toggleButton: {
      text: 'Search'
    },
    toggleButtonContainer: {
      selector: '.moj-search-toggle__toggle'
    }
  });
  /**
   * Search toggle config schema
   *
   * @satisfies {Schema<SearchToggleConfig>}
   */
  SearchToggle.schema = Object.freeze(/** @type {const} */{
    properties: {
      searchContainer: {
        type: 'object'
      },
      toggleButton: {
        type: 'object'
      },
      toggleButtonContainer: {
        type: 'object'
      }
    }
  });

  /**
   * @augments {ConfigurableComponent<SortableTableConfig>}
   */
  class SortableTable extends govukFrontend.ConfigurableComponent {
    /**
     * @param {Element | null} $root - HTML element to use for sortable table
     * @param {SortableTableConfig} [config] - Sortable table config
     */
    constructor($root, config = {}) {
      super($root, config);
      const $head = $root == null ? void 0 : $root.querySelector('thead');
      const $body = $root == null ? void 0 : $root.querySelector('tbody');
      if (!$head || !$body) {
        return this;
      }
      this.$head = $head;
      this.$body = $body;
      this.$caption = this.$root.querySelector('caption');
      this.$upArrow = `<svg width="22" height="22" focusable="false" aria-hidden="true" role="img" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M6.5625 15.5L11 6.63125L15.4375 15.5H6.5625Z" fill="currentColor"/>
</svg>`;
      this.$downArrow = `<svg width="22" height="22" focusable="false" aria-hidden="true" role="img" vviewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M15.4375 7L11 15.8687L6.5625 7L15.4375 7Z" fill="currentColor"/>
</svg>`;
      this.$upDownArrow = `<svg width="22" height="22" focusable="false" aria-hidden="true" role="img" vviewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M8.1875 9.5L10.9609 3.95703L13.7344 9.5H8.1875Z" fill="currentColor"/>
<path d="M13.7344 12.0781L10.9609 17.6211L8.1875 12.0781H13.7344Z" fill="currentColor"/>
</svg>`;
      this.$headings = this.$head ? Array.from(this.$head.querySelectorAll('th')) : [];
      this.createHeadingButtons();
      this.updateCaption();
      this.updateDirectionIndicators();
      this.createStatusBox();
      this.initialiseSortedColumn();
      this.$head.addEventListener('click', this.onSortButtonClick.bind(this));
    }
    createHeadingButtons() {
      for (const $heading of this.$headings) {
        if ($heading.hasAttribute('aria-sort')) {
          this.createHeadingButton($heading);
        }
      }
    }

    /**
     * @param {HTMLTableCellElement} $heading
     */
    createHeadingButton($heading) {
      const index = this.$headings.indexOf($heading);
      const $button = document.createElement('button');
      $button.setAttribute('type', 'button');
      $button.setAttribute('data-index', `${index}`);
      $button.textContent = $heading.textContent;
      $heading.textContent = '';
      $heading.appendChild($button);
    }
    createStatusBox() {
      this.$status = document.createElement('div');
      this.$status.setAttribute('aria-atomic', 'true');
      this.$status.setAttribute('aria-live', 'polite');
      this.$status.setAttribute('class', 'govuk-visually-hidden');
      this.$status.setAttribute('role', 'status');
      this.$root.insertAdjacentElement('afterend', this.$status);
    }
    initialiseSortedColumn() {
      var _$sortButton$getAttri;
      const $rows = this.getTableRowsArray();
      const $heading = this.$root.querySelector('th[aria-sort="ascending"], th[aria-sort="descending"]');
      const $sortButton = $heading == null ? void 0 : $heading.querySelector('button');
      const sortDirection = $heading == null ? void 0 : $heading.getAttribute('aria-sort');
      const columnNumber = Number.parseInt((_$sortButton$getAttri = $sortButton == null ? void 0 : $sortButton.getAttribute('data-index')) != null ? _$sortButton$getAttri : '0', 10);
      if (!$heading || !$sortButton || !(sortDirection === 'ascending' || sortDirection === 'descending')) {
        return;
      }
      const $sortedRows = this.sort($rows, columnNumber, sortDirection);
      this.addRows($sortedRows);
    }

    /**
     * @param {MouseEvent} event - Click event
     */
    onSortButtonClick(event) {
      var _$button$getAttribute;
      const $target = /** @type {HTMLElement} */event.target;
      const $button = $target.closest('button');
      if (!$button || !($button instanceof HTMLButtonElement) || !$button.parentElement) {
        return;
      }
      const $heading = $button.parentElement;
      const sortDirection = $heading.getAttribute('aria-sort');
      const columnNumber = Number.parseInt((_$button$getAttribute = $button == null ? void 0 : $button.getAttribute('data-index')) != null ? _$button$getAttribute : '0', 10);
      const newSortDirection = sortDirection === 'none' || sortDirection === 'descending' ? 'ascending' : 'descending';
      const $rows = this.getTableRowsArray();
      const $sortedRows = this.sort($rows, columnNumber, newSortDirection);
      this.addRows($sortedRows);
      this.removeButtonStates();
      this.updateButtonState($button, newSortDirection);
      this.updateDirectionIndicators();
    }
    updateCaption() {
      if (!this.$caption) {
        return;
      }
      let assistiveText = this.$caption.querySelector('.govuk-visually-hidden');
      if (assistiveText) {
        return;
      }
      assistiveText = document.createElement('span');
      assistiveText.classList.add('govuk-visually-hidden');
      assistiveText.textContent = ' (column headers with buttons are sortable).';
      this.$caption.appendChild(assistiveText);
    }

    /**
     * @param {HTMLButtonElement} $button
     * @param {string} direction
     */
    updateButtonState($button, direction) {
      if (!(direction === 'ascending' || direction === 'descending')) {
        return;
      }
      $button.parentElement.setAttribute('aria-sort', direction);
      let message = this.config.statusMessage;
      message = message.replace(/%heading%/, $button.textContent);
      message = message.replace(/%direction%/, this.config[`${direction}Text`]);
      this.$status.textContent = message;
    }
    updateDirectionIndicators() {
      for (const $heading of this.$headings) {
        const $button = /** @type {HTMLButtonElement} */
        $heading.querySelector('button');
        if ($heading.hasAttribute('aria-sort') && $button) {
          var _$button$querySelecto;
          const direction = $heading.getAttribute('aria-sort');
          (_$button$querySelecto = $button.querySelector('svg')) == null || _$button$querySelecto.remove();
          switch (direction) {
            case 'ascending':
              $button.insertAdjacentHTML('beforeend', this.$upArrow);
              break;
            case 'descending':
              $button.insertAdjacentHTML('beforeend', this.$downArrow);
              break;
            default:
              $button.insertAdjacentHTML('beforeend', this.$upDownArrow);
          }
        }
      }
    }
    removeButtonStates() {
      for (const $heading of this.$headings) {
        $heading.setAttribute('aria-sort', 'none');
      }
    }

    /**
     * @param {HTMLTableRowElement[]} $rows
     */
    addRows($rows) {
      for (const $row of $rows) {
        this.$body.append($row);
      }
    }
    getTableRowsArray() {
      return Array.from(this.$body.querySelectorAll('tr'));
    }

    /**
     * @param {HTMLTableRowElement[]} $rows
     * @param {number} columnNumber
     * @param {string} sortDirection
     */
    sort($rows, columnNumber, sortDirection) {
      return $rows.sort(($rowA, $rowB) => {
        const $tdA = $rowA.querySelectorAll('td, th')[columnNumber];
        const $tdB = $rowB.querySelectorAll('td, th')[columnNumber];
        if (!$tdA || !$tdB || !($tdA instanceof HTMLElement) || !($tdB instanceof HTMLElement)) {
          return 0;
        }
        const valueA = sortDirection === 'ascending' ? this.getCellValue($tdA) : this.getCellValue($tdB);
        const valueB = sortDirection === 'ascending' ? this.getCellValue($tdB) : this.getCellValue($tdA);
        return !(typeof valueA === 'number' && typeof valueB === 'number') ? valueA.toString().localeCompare(valueB.toString()) : valueA - valueB;
      });
    }

    /**
     * @param {HTMLElement} $cell
     */
    getCellValue($cell) {
      const val = $cell.getAttribute('data-sort-value') || $cell.innerHTML;
      const valAsNumber = Number(val);
      return Number.isFinite(valAsNumber) ? valAsNumber // Exclude invalid numbers, infinity etc
      : val;
    }

    /**
     * Name for the component used when initialising using data-module attributes.
     */
  }

  /**
   * Sortable table config
   *
   * @typedef {object} SortableTableConfig
   * @property {string} [statusMessage] - Status message
   * @property {string} [ascendingText] - Ascending text
   * @property {string} [descendingText] - Descending text
   */

  /**
   * @import { Schema } from 'govuk-frontend/dist/govuk/common/configuration.mjs'
   */
  SortableTable.moduleName = 'moj-sortable-table';
  /**
   * Sortable table config
   *
   * @type {SortableTableConfig}
   */
  SortableTable.defaults = Object.freeze({
    statusMessage: 'Sort by %heading% (%direction%)',
    ascendingText: 'ascending',
    descendingText: 'descending'
  });
  /**
   * Sortable table config schema
   *
   * @satisfies {Schema<SortableTableConfig>}
   */
  SortableTable.schema = Object.freeze(/** @type {const} */{
    properties: {
      statusMessage: {
        type: 'string'
      },
      ascendingText: {
        type: 'string'
      },
      descendingText: {
        type: 'string'
      }
    }
  });

  /**
   * @param {Config} [config]
   */
  function initAll(config) {
    for (const Component of [AddAnother, Alert, ButtonMenu, DatePicker, MultiSelect, PasswordReveal, RichTextEditor, SearchToggle, SortableTable]) {
      govukFrontend.createAll(Component, undefined, config);
    }
  }

  /**
   * @typedef {Parameters<typeof GOVUKFrontend.initAll>[0]} Config
   */

  /**
   * @import * as GOVUKFrontend from 'govuk-frontend'
   */

  exports.AddAnother = AddAnother;
  exports.Alert = Alert;
  exports.ButtonMenu = ButtonMenu;
  exports.DatePicker = DatePicker;
  exports.FilterToggleButton = FilterToggleButton;
  exports.FormValidator = FormValidator;
  exports.MultiFileUpload = MultiFileUpload;
  exports.MultiSelect = MultiSelect;
  exports.PasswordReveal = PasswordReveal;
  exports.RichTextEditor = RichTextEditor;
  exports.SearchToggle = SearchToggle;
  exports.SortableTable = SortableTable;
  exports.initAll = initAll;
  exports.version = version;

}));
//# sourceMappingURL=all.bundle.js.map
