<script lang="ts">
	// NOTE: Best docs https://tiptap.dev/docs/editor/api/editor
	//
	import { createEventDispatcher, onDestroy, onMount } from 'svelte';
	import { type Props, variants } from './index';
	import { Editor } from '@tiptap/core';
	import StarterKit from '@tiptap/starter-kit';
	import Link from '@tiptap/extension-link'
	import { cn } from '$lib/utils';
	import Placeholder from '@tiptap/extension-placeholder';

	type $$Props = Props;
	let className: $$Props['class'] = undefined;
	export { className as class };

	export let content: string = '';
	export let editable: boolean = true;
	export let placeholder: string = '';

	$: if (editor && content !== editor.getHTML()) {
		editor.chain().setContent(content, false, { preserveWhitespace: 'full' }).run();
	}

	$: {
		if (editor) {
			editor.setEditable(editable);
		}
		// editor.on('update', ({ content }) => {
		// 	// The content has changed.
		// 	content
		// });
	}

	let element: Element;
	let editor: Editor;

	onMount(() => {
		editor = new Editor({
			element: element,
			extensions: [
				StarterKit,
				Placeholder.configure({
					placeholder: placeholder,
					emptyEditorClass: 'is-editor-empty',
				}),
				Link.configure({
					openOnClick: false,
					autolink: true,
					defaultProtocol: 'https',
					protocols: ['http', 'https'],
					isAllowedUri: (url, ctx) => {
					try {
						// construct URL
						const parsedUrl = url.includes(':') ? new URL(url) : new URL(`${ctx.defaultProtocol}://${url}`)

						// use default validation
						if (!ctx.defaultValidate(parsedUrl.href)) {
						return false
						}

						// disallowed protocols
						const disallowedProtocols = ['ftp', 'file', 'mailto']
						const protocol = parsedUrl.protocol.replace(':', '')

						if (disallowedProtocols.includes(protocol)) {
						return false
						}

						// only allow protocols specified in ctx.protocols
						const allowedProtocols = ctx.protocols.map(p => (typeof p === 'string' ? p : p.scheme))

						if (!allowedProtocols.includes(protocol)) {
						return false
						}

						// disallowed domains
						const disallowedDomains = ['example-phishing.com', 'malicious-site.net']
						const domain = parsedUrl.hostname

						if (disallowedDomains.includes(domain)) {
						return false
						}

						// all checks have passed
						return true
					} catch (error) {
						return false
					}
					},
					shouldAutoLink: url => {
					try {
						// construct URL
						const parsedUrl = url.includes(':') ? new URL(url) : new URL(`https://${url}`)

						// only auto-link if the domain is not in the disallowed list
						const disallowedDomains = ['example-no-autolink.com', 'another-no-autolink.com']
						const domain = parsedUrl.hostname

						return !disallowedDomains.includes(domain)
					} catch (error) {
						return false
					}
					},

				}),
			],
			content: content,
			onTransaction: () => {
				// force re-render so `editor.isActive` works as expected
				editor = editor;

				if (content === editor.getHTML()) {
					return;
				}

				content = editor.getHTML();
			},
		});

		editor.setOptions({
			editorProps: {
				attributes: {
					class: 'rounded-xl ' + cn(variants({ className })),
				},
			},
		});
	});

	onDestroy(() => {
		if (editor) {
			editor.destroy();
		}
	});
</script>

<div bind:this={element}></div>
