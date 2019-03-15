<script>
export default {
  name: 'CodeBlockCopyButton'
}
</script>

<style>
  .code-block-copy-button {
    cursor: pointer;
    display: inline-block;
    position: absolute;
    z-index: 999;
    top: 10px;
    right: 8px;
    width: 20px;
    height: 30px;
    content: url(../public/copy-to-clipboard-icon.svg);
    transition: opacity .3s, transform .2s;
  }
  .code-block-copy-button:active {
    transform: scale(.8);
  }
  .code-block-copy-button:hover {
    opacity: .5;
  }
  .code-block-copy-button-offset {
    top: 34px;
  }
</style>
