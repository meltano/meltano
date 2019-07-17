<script>
export default {
	name: 'TooltipCircle',
	props: {
		text: {
			type: String,
			required: true
		}
	}
}
</script>

<template>
	<button
		class="button tooltip is-tooltip-multiline"
		:class="$style['tooltip-circle']"
		:data-tooltip="text"
	>
		<span :class="$style.tooltipText">?</span>
	</button>
</template>

<style lang="scss" module>
.tooltip-circle {
	width: 15px;
	height: 15px;
	padding: 0;
	font-size: 0.7rem;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	background-color: #bbb;
	color: #fff;
}

.tooltipText {
	margin-top: -2px;
}
</style>
