import json

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from core.civilization.person.tool.base import BaseTool, BuildParams, UseParams


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

    def use(self, command: str, params: UseParams) -> str:
        # command: [open, scroll, move, click, write, close]
        # params: [url, position, css selector, css selector, {css selector: input}, empty]

        try:
            method = getattr(self, command)
            method(params.input)
            return self._read()
        except KeyError:
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
            self.driver.execute_script("window.scrollX + ',' + window.scrollY").split(
                ","
            ),
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
            "xpath", "//*[not(self::script) and not(self::style)]"
        ):
            is_included = (
                element.location["x"] > x
                and element.location["y"] > y
                and element.location["x"] + element.size["width"] < x + width
                and element.location["y"] + element.size["height"] < y + height
                and element.location["x"] > 0
                and element.location["y"] > 0
                and element.size["height"] > 0
                and element.size["width"] > 0
            )
            if not is_included:
                continue
            if element.tag_name in self.writable_tag.keys():
                elements.append(
                    (
                        element,
                        element.get_attribute(self.writable_tag[element.tag_name]),
                    )
                )
            elif element.text != "":
                if len(element.find_elements("xpath", "./child::*")) == 0:
                    elements.append((element, element.text))

        contents = []
        contents.append(
            "This is information on the elements of url below, and contains the coordinates, contents, and css_selector of each element. "
            "You can move, click, and write with css_selector."
        )
        contents.append(self.driver.current_url)
        contents.append(f"page height, width: {page_height}, {page_width}")
        contents.append(f"scroll x, y, height, width: {x}, {y}, {height}, {width}")
        contents.append("\n(x, y, height, width) contents, css_selector")

        self._init_css_selector()

        for (element, content) in elements:
            position = f"({element.location['x']}, {element.location['y']}, {element.size['height']}, {element.size['width']})"
            css_selector = self.driver.execute_script(
                f"{self.css_selector}; return cssSelector(arguments[0]);", element
            )
            self.css_selectors[css_selector] = element
            contents.append(f"{position} {content}, {css_selector}")

        contents = "\n".join(contents)
        if contents == self.before_contents:
            return "No change"

        self.before_contents = contents
        return contents
