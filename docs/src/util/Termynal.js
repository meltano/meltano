import React from "react";

const Termynal = ({ children }) => {
  class Termynal {
    constructor(container = "#termynal", options = {}) {
      this.container =
        typeof container === "string"
          ? document.querySelector(container)
          : container;
      this.pfx = `data-${options.prefix || "ty"}`;
      this.startDelay =
        options.startDelay ||
        parseFloat(this.container.getAttribute(`${this.pfx}-startDelay`)) ||
        600;
      this.typeDelay =
        options.typeDelay ||
        parseFloat(this.container.getAttribute(`${this.pfx}-typeDelay`)) ||
        90;
      this.lineDelay =
        options.lineDelay ||
        parseFloat(this.container.getAttribute(`${this.pfx}-lineDelay`)) ||
        1500;
      this.progressLength =
        options.progressLength ||
        parseFloat(this.container.getAttribute(`${this.pfx}-progressLength`)) ||
        40;
      this.progressChar =
        options.progressChar ||
        this.container.getAttribute(`${this.pfx}-progressChar`) ||
        "█";
      this.progressPercent =
        options.progressPercent ||
        parseFloat(
          this.container.getAttribute(`${this.pfx}-progressPercent`)
        ) ||
        100;
      this.cursor =
        options.cursor ||
        this.container.getAttribute(`${this.pfx}-cursor`) ||
        "▋";
      this.lineData = this.lineDataToElements(options.lineData || []);
      if (!options.noInit) this.init();
    }

    /**
     * Initialise the widget, get lines, clear container and start animation.
     */
    init() {
      // Appends dynamically loaded lines to existing line elements.
      this.lines = [...this.container.querySelectorAll(`[${this.pfx}]`)].concat(
        this.lineData
      );

      /**
       * Calculates width and height of Termynal container.
       * If container is empty and lines are dynamically loaded, defaults to browser `auto` or CSS.
       */
      const containerStyle = getComputedStyle(this.container);
      this.container.style.width =
        containerStyle.width !== "0px" ? containerStyle.width : undefined;
      this.container.style.minHeight =
        containerStyle.height !== "0px" ? containerStyle.height : undefined;

      this.container.setAttribute("data-termynal", "");
      this.container.innerHTML = "";
      this.start();
    }

    /**
     * Start the animation and rener the lines depending on their data attributes.
     */
    async start() {
      await this._wait(this.startDelay);

      for (let line of this.lines) {
        const type = line.getAttribute(this.pfx);
        const delay = line.getAttribute(`${this.pfx}-delay`) || this.lineDelay;

        if (type == "input") {
          line.setAttribute(`${this.pfx}-cursor`, this.cursor);
          await this.type(line);
          await this._wait(delay);
        } else if (type == "progress") {
          await this.progress(line);
          await this._wait(delay);
        } else {
          this.container.appendChild(line);
          await this._wait(delay);
        }

        line.removeAttribute(`${this.pfx}-cursor`);
      }
    }

    /**
     * Animate a typed line.
     * @param {Node} line - The line element to render.
     */
    async type(line) {
      const chars = [...line.textContent];
      const delay =
        line.getAttribute(`${this.pfx}-typeDelay`) || this.typeDelay;
      line.textContent = "";
      this.container.appendChild(line);

      for (let char of chars) {
        await this._wait(delay);
        line.textContent += char;
      }
    }

    /**
     * Animate a progress bar.
     * @param {Node} line - The line element to render.
     */
    async progress(line) {
      const progressLength =
        line.getAttribute(`${this.pfx}-progressLength`) || this.progressLength;
      const progressChar =
        line.getAttribute(`${this.pfx}-progressChar`) || this.progressChar;
      const chars = progressChar.repeat(progressLength);
      const progressPercent =
        line.getAttribute(`${this.pfx}-progressPercent`) ||
        this.progressPercent;
      line.textContent = "";
      this.container.appendChild(line);

      for (let i = 1; i < chars.length + 1; i++) {
        await this._wait(this.typeDelay);
        const percent = Math.round((i / chars.length) * 100);
        line.textContent = `${chars.slice(0, i)} ${percent}%`;
        if (percent > progressPercent) {
          break;
        }
      }
    }

    /**
     * Helper function for animation delays, called with `await`.
     * @param {number} time - Timeout, in ms.
     */
    _wait(time) {
      return new Promise((resolve) => setTimeout(resolve, time));
    }

    /**
     * Converts line data objects into line elements.
     *
     * @param {Object[]} lineData - Dynamically loaded lines.
     * @param {Object} line - Line data object.
     * @returns {Element[]} - Array of line elements.
     */
    lineDataToElements(lineData) {
      return lineData.map((line) => {
        let div = document.createElement("div");
        div.innerHTML = `<span ${this._attributes(line)}>${
          line.value || ""
        }</span>`;

        return div.firstElementChild;
      });
    }

    /**
     * Helper function for generating attributes string.
     *
     * @param {Object} line - Line data object.
     * @returns {string} - String of attributes.
     */
    _attributes(line) {
      let attrs = "";
      for (let prop in line) {
        attrs += this.pfx;

        if (prop === "type") {
          attrs += `="${line[prop]}" `;
        } else if (prop !== "value") {
          attrs += `-${prop}="${line[prop]}" `;
        }
      }

      return attrs;
    }
  }

  document.querySelectorAll(".use-termynal").forEach((node) => {
    node.style.display = "block";
    // eslint-disable-next-line no-undef
    new Termynal(node, {
      lineDelay: 500,
    });
  });

  const progressLiteralStart = "---> 100%";
  const promptLiteralStart = "$ ";
  const customPromptLiteralStart = "# ";
  const termynalActivateClass = "termy";
  const codeThingy = "```";
  const waitStart = "<---";

  let termynals = [];

  function createTermynals() {
    document.querySelectorAll(`.${termynalActivateClass}`).forEach((node) => {
      const text = node.textContent;
      const lines = text.split("\n");
      const useLines = [];
      let buffer = [];
      function saveBuffer() {
        if (buffer.length) {
          let isBlankSpace = true;
          buffer.forEach((line) => {
            if (line) {
              isBlankSpace = false;
            }
          });
          let dataValue = {};
          if (isBlankSpace) {
            dataValue["delay"] = 0;
          }
          if (buffer[buffer.length - 1] === "") {
            // A last single <br> won't have effect
            // so put an additional one
            buffer.push("");
          }
          const bufferValue = buffer.join("<br>");
          dataValue["value"] = bufferValue;
          useLines.push(dataValue);
          buffer = [];
        }
      }
      for (let line of lines) {
        if (line === progressLiteralStart) {
          saveBuffer();
          useLines.push({
            type: "progress",
          });
        } else if (line.startsWith(promptLiteralStart)) {
          saveBuffer();
          const value = line.replace(promptLiteralStart, "").trimEnd();
          useLines.push({
            type: "input",
            value: value,
          });
        } else if (line.startsWith("// ")) {
          saveBuffer();
          const value = "💬 " + line.replace("// ", "").trimEnd();
          useLines.push({
            value: value,
            class: "termynal-comment",
            delay: 0,
          });
        } else if (line == waitStart) {
          saveBuffer();
          useLines.push({
            type: "wait",
            delay: 1,
            value: "<br />",
          });
        } else if (line.startsWith(customPromptLiteralStart)) {
          saveBuffer();
          const promptStart = line.indexOf(promptLiteralStart);
          if (promptStart === -1) {
            console.error("Custom prompt found but no end delimiter", line);
          }
          const prompt = line
            .slice(0, promptStart)
            .replace(customPromptLiteralStart, "");
          let value = line.slice(promptStart + promptLiteralStart.length);
          useLines.push({
            type: "input",
            value: value,
            prompt: prompt,
          });
        } else if (line.startsWith(codeThingy)) {
          saveBuffer();
        } else {
          buffer.push(line);
        }
      }
      saveBuffer();
      const div = document.createElement("div");
      node.replaceWith(div);
      // eslint-disable-next-line no-undef
      const termynal = new Termynal(div, {
        lineData: useLines,
        noInit: true,
        lineDelay: 500,
      });
      termynals.push(termynal);
    });
  }

  function loadVisibleTermynals() {
    termynals = termynals.filter((termynal) => {
      if (termynal.container.getBoundingClientRect().top - innerHeight <= 0) {
        termynal.init();
        return false;
      }
      return true;
    });
  }
  window.addEventListener("scroll", loadVisibleTermynals);
  createTermynals();
  loadVisibleTermynals();

  return <div id="termynal">{children}</div>;
};

export default Termynal;
