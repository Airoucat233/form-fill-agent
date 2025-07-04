// markdown-it plugin for wrapping <pre> ... </pre>.
//
// If your plugin was chained before preWrapper, you can add additional eleemnt directly.
// If your plugin was chained after preWrapper, you can use these slots:
//   1. <!--beforebegin-->
//   2. <!--afterbegin-->
//   3. <!--beforeend-->
//   4. <!--afterend-->

export default md => {
    const fence = md.renderer.rules.fence
    md.renderer.rules.fence = (...args) => {
      const [tokens, idx] = args
      const token = tokens[idx]
      if(!token.content.trim()){
        return ''
      }
      const rawCode = fence(...args)
      return `<!--beforebegin--><div class="language-${token.info.trim() || 'code'} extra-class">` +
      `<!--afterbegin-->${rawCode}<!--beforeend--></div><!--afterend-->`
    }
  }