<script>
import { mapGetters } from 'vuex'
import InputDateIso8601 from '@/components/generic/InputDateIso8601'
import TooltipCircle from '@/components/generic/TooltipCircle'

import utils from '@/utils/utils'

export default {
	name: 'ConnectorSettings',
	components: {
		InputDateIso8601,
		TooltipCircle
	},
	props: {
		fieldClass: { type: String },
		configSettings: {
			type: Object,
			required: true,
			default: () => {}
		}
	},
	watch: {
		configSettings: {
			handler(newVal, oldVal) {
				/**
				 * Improve account UX by auto-detecting Account ID via URL
				 */

				let accountInput = newVal.config.account
				let domainFlag = 'snowflakecomputing.com'
				let domainLocation = accountInput.indexOf(domainFlag)

				// If the domain exists in user input, assume URL
				if (domainLocation > -1) {
					let shortenedUrl = accountInput.slice(
						0,
						domainLocation + domainFlag.length
					)

					// Clean up URL if http is detected
					if (shortenedUrl.indexOf('http') > -1) {
						shortenedUrl = shortenedUrl.slice(shortenedUrl.indexOf('//') + 2)
					}

					// This could eventually parse data like region if needed
					let accountId = shortenedUrl.split('.')[0]

					this.configSettings.config.account = accountId
				} else {
					this.configSettings.config.account = newVal.config.account
				}
			},
			deep: true
		}
	},
	computed: {
		...mapGetters('configuration', ['getIsConfigSettingValid']),
		getCleanedLabel() {
			return value => utils.titleCase(utils.underscoreToSpace(value))
		},
		getIsOfKindBoolean() {
			return kind => kind === 'boolean'
		},
		getIsOfKindDate() {
			return kind => kind === 'date_iso8601'
		},
		getIsOfKindTextBased() {
			return kind =>
				!this.getIsOfKindBoolean(kind) && !this.getIsOfKindDate(kind)
		},
		getTextBasedInputType() {
			let type = 'text'
			return setting => {
				switch (setting.kind) {
					case 'password':
						type = 'password'
						break
					case 'email':
						type = 'email'
						break
					default:
						type = utils.inferInputType(setting.name, 'text')
						break
				}
				return type
			}
		},
		labelClass() {
			return this.fieldClass || 'is-normal'
		},
		successClass() {
			return setting =>
				this.getIsConfigSettingValid(setting)
					? 'is-success has-text-success'
					: null
		}
	}
}
</script>

<template>
	<div>
		<slot name="top" />
		<div
			class="field is-horizontal"
			v-for="setting in configSettings.settings"
			:key="setting.name"
		>
			<div :class="['is-flex', 'field-label', labelClass]">
				<label class="label">{{
					setting.label || getCleanedLabel(setting.name)
				}}</label>
				<TooltipCircle
					v-if="getCleanedLabel(setting.name) === 'Account'"
					text="Paste your login URL if you don't know your account ID."
					style="margin-left: 2px"
				/>
			</div>
			<div class="field-body">
				<div class="field">
					<div class="control is-expanded">
						<!-- Boolean -->
						<label v-if="getIsOfKindBoolean(setting.kind)" class="checkbox">
							<input
								v-model="configSettings.config[setting.name]"
								:class="successClass(setting)"
								type="checkbox"
							/>
						</label>

						<!-- Date -->
						<InputDateIso8601
							v-else-if="getIsOfKindDate(setting.kind)"
							v-model="configSettings.config[setting.name]"
							:name="setting.name"
							input-classes="is-small"
						/>

						<!-- Text / Password / Email -->
						<input
							v-else-if="getIsOfKindTextBased(setting.kind)"
							v-model="configSettings.config[setting.name]"
							:class="['input', fieldClass, successClass(setting)]"
							@focus="$event.target.select()"
							:type="getTextBasedInputType(setting)"
							:placeholder="setting.value || setting.name"
						/>
					</div>
					<p v-if="setting.description" class="help is-italic">
						{{ setting.description }}
					</p>
					<p v-if="setting.documentation" class="help">
						<a :href="setting.documentation">More Info.</a>
					</p>
				</div>
			</div>
		</div>
		<slot name="bottom" />
	</div>
</template>

<style lang="scss"></style>
