<script>
export default {
    name: 'LogoContainer',
    props: {
        imageAlt: {
            type: String,
            required: true
        },
        imageUrl: {
            type: String,
            required: true
        },
        label: {
            type: String,
            required: true
        }
    }
}
</script>

<template>
	<div class="logo-container">
        <img :src="imageUrl" :alt="imageAlt">
        <a :href="imageUrl" class="logo-container__link">{{ label }}</a>
    </div>
</template>

<style>
.logo-container {
	border: 1px solid #e7e7e7;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	text-align: center;
}

.logo-container__link {
	display: block;
	padding: 14px;
	border-top: 1px solid #e7e7e7;
}
</style>
