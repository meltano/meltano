<script>
export default {
    name: 'LogoList',
    data() {
        return {
            logos: [
                {
                    url: '/Meltano-Melty-Logo.png',
                    alt: 'Meltano Logo (Purple)',
                    label: 'Meltano Logo'
                },
                                {
                    url: '/Meltano-Melty-logo-stacked.png',
                    alt: 'Meltano Logo (Purple)',
                    label: 'Meltano Logo'
                },
                {
                    url: 'Meltano-Melty-logo-stacked-black.svg',
                    alt: 'Meltano Logo (Purple)',
                    label: 'Meltano Logo'
                },
                {
                    url: 'Meltano-Melty-logo-black.svg',
                    alt: 'Meltano Logo (Purple)',
                    label: 'Meltano Logo'
                },
                {
                    url: '/Meltano-Melty-Logo.png',
                    alt: 'Meltano Logo (Purple)',
                    label: 'Meltano Logo',
                    theme: 'dark'
                }
            ]
        }
    }
}
</script>

<template>
	<div class="logo-list">
        <LogoListItem v-for="(logo, index) in logos"
            class="logo-list__item"
            :class="{ 'logo-list__item--dark': logo.theme === 'dark' }"
            :imageUrl="logo.url"
            :imageAlt="logo.alt"
            :label="logo.label"
            :key="`meltano-logo-${index}`"
        />
    </div>
</template>

<style>
.logo-list {
	padding-top: 1rem;
}

.logo-list__item {
	margin-bottom: 1rem;
}

.logo-list__item--dark {
	background-color: #333;
}

@media screen and (min-width: 768px) {
	.logo-list {
		display: flex;
		flex-wrap: wrap;
	}

	.logo-list__item {
		flex: 1 1 auto;
		margin-right: 0.5rem;
		margin-left: 0.5rem;
	}

	.logo-list__item:last-child {
		margin-right: 0;
	}
}
</style>
