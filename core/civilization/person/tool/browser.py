import json

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.remote_connection import LOGGER, logging

from core.civilization.person.tool.base import BaseTool, BuildParams, UseParams
from core.logging import logger
from core.logging.ansi import Color

LOGGER.setLevel(logging.WARNING)


class Browser(BaseTool):
    name = "browser"
    instruction = (
        "Surfing the web on a browser. "
        "Instruction should be one valid command. (ex. open, scroll, move, click, write, close) "
        "Extra should be a valid input for that command. "
        # "You can also enter the key directly through the write command, such as Keys.RETURN and Keys.SHIFT. " # TODO
        "open: <url>, scroll: <position>, move: <id>, click: <id>, write: <{id: input}>, close: <empty> "
        'ex. open: https://www.google.com, scroll: 0,0, move: 3, click: 4, write: {5: "hello"}, close: '
        "Output will be the page's contents. "
    )
    color = Color.rgb(0, 0, 255)

    css_selector = """var cssSelector = function(el) {
        if (!(el instanceof Element)) 
            return;
        var path = [];
        while (el.nodeType === Node.ELEMENT_NODE) {
            var selector = el.nodeName.toLowerCase();
            if (el.id) {
                selector += '#' + el.id;
                path.unshift(selector);
                break;
            } else {
                var sib = el, nth = 1;
                var has_next = sib.nextElementSibling != null;
                while (sib = sib.previousElementSibling) {
                    if (sib.nodeName.toLowerCase() == selector)
                        nth++;
                }
                if (nth != 1 || has_next)
                    selector += "["+nth+"]";
            }
            path.unshift(selector);
            el = el.parentNode;
        }
        return path.join(" > ");
    }"""
    writable_tag = {"textarea": "placeholder", "input": "type"}

    _options: webdriver.ChromeOptions = webdriver.ChromeOptions()
    _options.add_experimental_option("prefs", {"intl.accept_languages": "en-GB"})

    _driver: webdriver.Chrome = webdriver.Chrome(
        executable_path="chromedriver", options=_options
    )
    _action_chains: ActionChains = ActionChains(_driver)
    css_selectors = {}
    before_contents = ""

    def build(self, params: BuildParams) -> str:
        pass

    @logger.disable
    def use(self, command: str, params: UseParams) -> str:
        # command: [open, scroll, move, click, write, close] # TODO: send_keys
        # params: [url, position, css selector, css selector, {css selector: input}, empty]

        try:
            method = getattr(self, command)
            method(params.input)
            return self._read()
        except AttributeError:
            return f"Unknown command type '{command}', expected one of: open, scroll, move, click, write, close"

    def open(self, url: str):
        for handle in self._driver.window_handles:
            self._driver.switch_to.window(handle)
            if self._driver.current_url == url:
                return

        if self._driver.current_url != "data:,":
            self._driver.execute_script("window.open('');")
        self._driver.get(url)

    def scroll(self, position: str):
        try:
            delta_x, delta_y = map(int, position.split(","))
        except IndexError:
            return f"Invalid position '{position}'. Expected format: 'x,y'"

        position_x, position_y = map(
            int,
            self._driver.execute_script(
                "return window.scrollX + ',' + window.scrollY"
            ).split(","),
        )
        self._driver.execute_script(
            f"window.scrollTo({position_x + delta_x},{position_y + delta_y})"
        )

    def move(self, css_selector: str):
        try:
            element = self.css_selectors[css_selector]
        except KeyError:
            return f"Unknown css selector '{css_selector}'"

        self._action_chains.move_to_element(element).perform()

    def click(self, css_selector: str):
        try:
            element = self.css_selectors[css_selector]
        except KeyError:
            return f"Unknown css selector '{css_selector}'"

        self._action_chains.click(element).perform()
        self._init_css_selector()
        self._driver.implicitly_wait(3)

    def write(self, contents: str):
        try:
            contents = json.loads(contents)
        except json.decoder.JSONDecodeError:
            return f"Invalid contents '{contents}'. Expected JSON format."

        for css_selector, content in contents.items():
            try:
                element = self.css_selectors[css_selector]
            except KeyError:
                return f"Unknown css selector '{css_selector}'"

            if element.tag_name == "input":
                element.clear()
                element.send_keys(content)
            elif element.tag_name == "textarea":
                element.clear()
                element.send_keys(content)
            else:
                return f"Unknown tag name '{element.tag_name}'"

    def close(self, _: str):
        self._driver.close()
        self._driver.switch_to.window(self._driver.window_handles[-1])

    def _init_css_selector(self):
        self.css_selectors = {}

    def _read(self):
        x, y, height, width = map(
            int,
            self._driver.execute_script(
                "return window.scrollX + ',' + window.scrollY + ',' + window.innerHeight + ',' + window.innerWidth"
            ).split(","),
        )
        page_height, page_width = map(
            int,
            self._driver.execute_script(
                "return document.body.clientHeight + ',' + document.body.clientWidth"
            ).split(","),
        )

        elements = []
        for element in self._driver.find_elements(
            "xpath",
            (
                "//*[((not(contains(@style,'display:none')) "
                "and not(self::script) and not(self::style) "
                "and string-length(normalize-space(text())) > 0))"
                " or (self::textarea or self::input)]"
            ),
        ):
            location = element.location
            size = element.size
            is_included = (
                location["x"] > x
                and location["y"] > y
                and location["x"] + size["width"] < x + width
                and location["y"] + size["height"] < y + height
                and location["x"] > 0
                and location["y"] > 0
                and size["height"] > 0
                and size["width"] > 0
            )
            if not is_included or not is_included:
                continue
            if element.tag_name in self.writable_tag.keys():
                elements.append(
                    (
                        element,
                        element.get_attribute(self.writable_tag[element.tag_name]),
                    )
                )
            elif element.text != "":
                child = element.find_elements("xpath", "./*")
                element_text = (
                    element.text.split(child[0].text)[0]
                    if len(child) > 0 and len(child[0].text) > 0
                    else element.text
                )
                if element_text != "":
                    elements.append((element, element_text))

        contents = []
        contents.append(
            "This is information on the elements of url below, and contains id, contents of each element. "
            "You can move, click, and write with id."
        )
        contents.append(f"url: {self._driver.current_url}")
        contents.append(f"page height, width: {page_height}, {page_width}")
        contents.append(f"current x, y, height, width: {x}, {y}, {height}, {width}")
        contents.append("\nid. contents")

        self._init_css_selector()

        for i, (element, content) in enumerate(elements):
            css_selector = self._driver.execute_script(
                f"{self.css_selector}; return cssSelector(arguments[0]);", element
            )
            position = f"{element.location['x']}, {element.location['y']}, {element.size['height']}, {element.size['width']}"
            # contents.append(f"[{content}] {css_selector} ({position})")
            contents.append(f"{i}. {content}")

            self.css_selectors[str(i)] = element

        contents = "\n".join(contents)
        if contents == self.before_contents:
            return "No change"

        self.before_contents = contents
        return contents
