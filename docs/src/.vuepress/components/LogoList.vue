<script>
export default {
    name: 'LogoList',
    data() {
        return {
            logos: [
                {
                    url: '/Meltano-Melty-logo.svg',
                    alt: 'Meltano Logo (Purple)',
                    label: 'Meltano Logo with Text (Purple)',
                },
                {
                    url: '/Meltano-Melty-logo-black.svg',
                    alt: 'Meltano Logo (Black)',
                    label: 'Meltano Logo with Text (Black)',
                },
                {
                    url: '/Meltano-Melty-logo-white.svg',
                    alt: 'Meltano Logo (White)',
                    label: 'Meltano Logo with Text (White)',
                    theme: 'dark',
                },
                {
                    url: '/Meltano-Melty-logo-stacked.svg',
                    alt: 'Meltano Logo (Purple)',
                    label: 'Meltano Logo (Purple)',
                },
                {
                    url: '/Meltano-Melty-logo-stacked-black.svg',
                    alt: 'Meltano Logo (Black)',
                    label: 'Meltano Logo (Black)',
                },
                {
                    url: '/Meltano-Melty-logo-stacked-white.svg',
                    alt: 'Meltano Logo (White)',
                    label: 'Meltano Logo (White)',
                    theme: 'dark',
                },
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
