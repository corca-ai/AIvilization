import json

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.remote_connection import LOGGER, logging

from core.civilization.person.tool.base import BaseTool, BuildParams, UseParams
from core.logging import logger

LOGGER.setLevel(logging.WARNING)


class Browser(BaseTool):
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

    @logger.disable
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"intl.accept_languages": "en-GB"})
        self.driver = webdriver.Chrome(executable_path="chromedriver", options=options)
        self.action_chains = ActionChains(self.driver)
        self.css_selectors = {}
        self.before_contents = ""

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
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            if self.driver.current_url == url:
                return

        if self.driver.current_url != "data:,":
            self.driver.execute_script("window.open('');")
        self.driver.get(url)

    def scroll(self, position: str):
        try:
            delta_x, delta_y = map(int, position.split(","))
        except IndexError:
            return f"Invalid position '{position}'. Expected format: 'x,y'"

        position_x, position_y = map(
            int,
            self.driver.execute_script(
                "return window.scrollX + ',' + window.scrollY"
            ).split(","),
        )
        self.driver.execute_script(
            f"window.scrollTo({position_x + delta_x},{position_y + delta_y})"
        )

    def move(self, css_selector: str):
        try:
            element = self.css_selectors[css_selector]
        except KeyError:
            return f"Unknown css selector '{css_selector}'"

        self.action_chains.move_to_element(element).perform()

    def click(self, css_selector: str):
        try:
            element = self.css_selectors[css_selector]
        except KeyError:
            return f"Unknown css selector '{css_selector}'"

        self.action_chains.click(element).perform()
        self._init_css_selector()
        self.driver.implicitly_wait(3)

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
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def _init_css_selector(self):
        self.css_selectors = {}

    def _read(self):
        x, y, height, width = map(
            int,
            self.driver.execute_script(
                "return window.scrollX + ',' + window.scrollY + ',' + window.innerHeight + ',' + window.innerWidth"
            ).split(","),
        )
        page_height, page_width = map(
            int,
            self.driver.execute_script(
                "return document.body.clientHeight + ',' + document.body.clientWidth"
            ).split(","),
        )

        elements = []
        for element in self.driver.find_elements(
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
        contents.append(f"url: {self.driver.current_url}")
        contents.append(f"page height, width: {page_height}, {page_width}")
        contents.append(f"current x, y, height, width: {x}, {y}, {height}, {width}")
        contents.append("\nid. contents")

        self._init_css_selector()

        for i, (element, content) in enumerate(elements):
            css_selector = self.driver.execute_script(
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
