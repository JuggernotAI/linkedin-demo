import { s as styleTags, f as foldNodeProp, c as foldInside, p as parseMixed, t as tags, S as StreamLanguage } from './Index-bd21c2e8.js';
import { yaml } from './yaml-c63fc23d.js';
import './index-11cab7ad.js';
import './svelte/svelte.js';
import './Button-724396e3.js';
import './Index-045b93a3.js';
import './Check-1d114215.js';
import './Copy-ea46e0bf.js';
import './Download-ea83bae3.js';
import './BlockLabel-5c4e486a.js';
import './Empty-ff602cf2.js';
import './Example-ef3222e9.js';

const frontMatterFence = /^---\s*$/m;
const frontmatter = {
  defineNodes: [{ name: "Frontmatter", block: true }, "FrontmatterMark"],
  props: [
    styleTags({
      Frontmatter: [tags.documentMeta, tags.monospace],
      FrontmatterMark: tags.processingInstruction
    }),
    foldNodeProp.add({
      Frontmatter: foldInside,
      FrontmatterMark: () => null
    })
  ],
  wrap: parseMixed((node) => {
    const { parser } = StreamLanguage.define(yaml);
    if (node.type.name === "Frontmatter") {
      return {
        parser,
        overlay: [{ from: node.from + 4, to: node.to - 4 }]
      };
    }
    return null;
  }),
  parseBlock: [
    {
      name: "Frontmatter",
      before: "HorizontalRule",
      parse: (cx, line) => {
        let end = void 0;
        const children = new Array();
        if (cx.lineStart === 0 && frontMatterFence.test(line.text)) {
          children.push(cx.elt("FrontmatterMark", 0, 4));
          while (cx.nextLine()) {
            if (frontMatterFence.test(line.text)) {
              end = cx.lineStart + 4;
              break;
            }
          }
          if (end !== void 0) {
            children.push(cx.elt("FrontmatterMark", end - 4, end));
            cx.addElement(cx.elt("Frontmatter", 0, end, children));
          }
          return true;
        }
        return false;
      }
    }
  ]
};

export { frontmatter };
//# sourceMappingURL=frontmatter-258b7d0e.js.map
