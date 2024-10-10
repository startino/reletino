<script lang="ts">
	// NOTE: Best docs https://tiptap.dev/docs/editor/api/editor
	//
	import { createEventDispatcher, onDestroy, onMount } from 'svelte';
	import { type Props, variants } from './index';
	import { Editor } from '@tiptap/core';
	import { Color } from '@tiptap/extension-color'
	import ListItem from '@tiptap/extension-list-item'
	import TextStyle from '@tiptap/extension-text-style'
	import StarterKit from "@tiptap/starter-kit"
	import { cn } from '$lib/utils';

	type $$Props = Props;
	let className: $$Props['class'] = undefined;
	export { className as class };

	export let content: string = '';
	export let editable: boolean = true;
	export let plainText: boolean = false;

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
			extensions: [StarterKit],
			content: content,
			onTransaction: () => {
				// force re-render so `editor.isActive` works as expected
				editor = editor;

				if (content === editor.getHTML()) {
					return;
				}
				if (plainText) {
					content = editor.getText();
					return;
				}
				content = editor.getHTML();
			},
		});

		editor.setOptions({
			editorProps: {
				attributes: {
					class: cn(variants({ className })),
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
