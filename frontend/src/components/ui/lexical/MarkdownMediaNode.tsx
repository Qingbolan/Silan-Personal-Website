import React, { type JSX } from 'react';
import {
  MdastImportExtension,
  type MdastExportHandler,
  type MdastImportHandler,
  type MdastNode,
} from '@lexical/mdast';
import {
  $applyNodeReplacement,
  configExtension,
  DecoratorNode,
  defineExtension,
  type EditorConfig,
  type LexicalNode,
  type NodeKey,
  type SerializedLexicalNode,
  type Spread,
} from 'lexical';
import { isVideoResource, mediaUrl } from '../../../api/utils';

type SerializedMarkdownMediaNode = Spread<
  {
    altText: string;
    src: string;
    title?: string;
  },
  SerializedLexicalNode
>;

const trustedMediaSource = (source: string): string => {
  const normalized = source.trim();
  if (
    !normalized
    || !(
      normalized.startsWith('/')
      || normalized.startsWith('./')
      || normalized.startsWith('../')
      || normalized.startsWith('resources/')
      || normalized.startsWith('silan://resources/')
      || /^https?:\/\//i.test(normalized)
    )
  ) {
    return '';
  }
  return mediaUrl(normalized);
};

const MarkdownMedia: React.FC<{
  altText: string;
  src: string;
  title?: string;
}> = ({ altText, src, title }) => {
  const resolvedSource = trustedMediaSource(src);
  if (!resolvedSource) return null;

  return isVideoResource(src) ? (
    <video controls preload="metadata" aria-label={altText || title || 'Embedded video'}>
      <source src={resolvedSource} />
    </video>
  ) : (
    <img
      src={resolvedSource}
      alt={altText}
      title={title}
      loading="lazy"
      decoding="async"
    />
  );
};

export class MarkdownMediaNode extends DecoratorNode<JSX.Element> {
  __src: string;
  __altText: string;
  __title?: string;

  $config() {
    return this.config('markdown-media', { extends: DecoratorNode });
  }

  static clone(node: MarkdownMediaNode): MarkdownMediaNode {
    return new MarkdownMediaNode(node.__src, node.__altText, node.__title, node.__key);
  }

  static importJSON(serializedNode: SerializedMarkdownMediaNode): MarkdownMediaNode {
    return $createMarkdownMediaNode({
      altText: serializedNode.altText,
      src: serializedNode.src,
      title: serializedNode.title,
    });
  }

  constructor(src = '', altText = '', title?: string, key?: NodeKey) {
    super(key);
    this.__src = src;
    this.__altText = altText;
    this.__title = title;
  }

  createDOM(config: EditorConfig): HTMLElement {
    const element = document.createElement('span');
    const className = config.theme.image;
    if (typeof className === 'string') element.className = className;
    return element;
  }

  updateDOM(): false {
    return false;
  }

  isInline(): true {
    return true;
  }

  exportJSON(): SerializedMarkdownMediaNode {
    return {
      ...super.exportJSON(),
      altText: this.getAltText(),
      src: this.getSrc(),
      title: this.getTitle(),
    };
  }

  getSrc(): string {
    return this.getLatest().__src;
  }

  getAltText(): string {
    return this.getLatest().__altText;
  }

  getTitle(): string | undefined {
    return this.getLatest().__title;
  }

  getTextContent(): string {
    return this.getAltText();
  }

  decorate(): JSX.Element {
    return <MarkdownMedia src={this.__src} altText={this.__altText} title={this.__title} />;
  }
}

export const $createMarkdownMediaNode = ({
  altText,
  src,
  title,
}: {
  altText: string;
  src: string;
  title?: string;
}): MarkdownMediaNode => (
  $applyNodeReplacement(new MarkdownMediaNode(src, altText, title))
);

export const $isMarkdownMediaNode = (
  node: LexicalNode | null | undefined,
): node is MarkdownMediaNode => node instanceof MarkdownMediaNode;

type ImageAstNode = MdastNode & {
  alt?: string;
  identifier?: string;
  title?: string | null;
  type: 'image' | 'imageReference';
  url?: string;
};

const $importMedia: MdastImportHandler = (node, context) => {
  const image = node as ImageAstNode;
  if (image.type === 'image') {
    return $createMarkdownMediaNode({
      altText: image.alt ?? '',
      src: image.url ?? '',
      title: image.title ?? undefined,
    });
  }
  if (image.type === 'imageReference' && image.identifier) {
    const definition = context.getDefinition(image.identifier);
    if (definition) {
      return $createMarkdownMediaNode({
        altText: image.alt ?? '',
        src: definition.url,
        title: definition.title ?? undefined,
      });
    }
  }
  return null;
};

const $exportMedia: MdastExportHandler = (node) => {
  if (!$isMarkdownMediaNode(node)) return null;
  return {
    alt: node.getAltText(),
    title: node.getTitle() ?? null,
    type: 'image',
    url: node.getSrc(),
  } as MdastNode;
};

export const MarkdownMediaExtension = defineExtension({
  dependencies: [
    configExtension(MdastImportExtension, {
      exportRules: [{ $export: $exportMedia, type: 'markdown-media' }],
      importRules: [
        { $import: $importMedia, type: 'image' },
        { $import: $importMedia, type: 'imageReference' },
      ],
    }),
  ],
  name: 'silan/public-markdown-media',
  nodes: [MarkdownMediaNode],
});
