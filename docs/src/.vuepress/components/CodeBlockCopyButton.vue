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
    width: 24px;
    height: 24px;
    content: url(../public/copy-to-clipboard-icon.svg);
    background-color: #282c34;
    transition: transform .20s;
  }
  .code-block-copy-button:active {
    transform: scale(.8);
  }
</style>
