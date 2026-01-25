# Fumadocs Components Reference

This document serves as a reference for all Fumadocs UI components used in the better-py documentation. It provides installation guidance, usage examples, and implementation notes for each component.

## Table of Contents

- [Accordion](#accordion)
- [Auto Type Table](#auto-type-table)
- [Code Block](#code-block)
- [Files](#files)
- [GitHub Info](#github-info)
- [Inline TOC](#inline-toc)
- [Steps](#steps)
- [Tabs](#tabs)
- [Type Table](#type-table)

---

## Accordion

**Purpose**: Useful for FAQ sections and collapsible content areas.

**Installation**: Built into `@fumadocs-ui/components/accordion`

### Basic Usage

```tsx
import { Accordion, Accordions } from 'fumadocs-ui/components/accordion';

<Accordions type="single">
  <Accordion title="My Title">My Content</Accordion>
</Accordions>
```

### Linking to Accordion

Specify an `id` to allow direct navigation via URL hash. The accordion opens automatically when navigating with the hash parameter.

```tsx
<Accordions>
  <Accordion title="My Title" id="my-title">
    My Content
  </Accordion>
</Accordions>
```

**Note**: When an `id` is present, it's used as the value instead of the title.

### Props

**Accordions**
| Prop | Type | Description |
|------|------|-------------|
| type | `'single' \| 'multiple'` | Whether one or multiple accordions can be open |

**Accordion**
| Prop | Type | Description |
|------|------|-------------|
| title | `string` | The title displayed on the accordion header |
| id | `string` | Optional ID for hash linking |
| children | `ReactNode` | Content inside the accordion |

---

## Auto Type Table

**Purpose**: Automatically generates TypeScript type documentation tables from source files.

**Installation**: Requires additional package
```bash
npm i fumadocs-typescript
```

### Setup

Initialize the TypeScript compiler and add as MDX component:

**mdx-components.tsx**
```tsx
import defaultComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';
import { createGenerator, createFileSystemGeneratorCache } from 'fumadocs-typescript';
import { AutoTypeTable } from 'fumadocs-typescript/ui';

const generator = createGenerator({
  cache: createFileSystemGeneratorCache('.next/fumadocs-typescript'),
});

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultComponents,
    AutoTypeTable: (props) => <AutoTypeTable {...props} generator={generator} />,
    ...components,
  };
}
```

### Usage

**From TypeScript file**:
```tsx
<AutoTypeTable path="./path/to/file.ts" name="MyInterface" />
```

**From inline type**:
```tsx
<AutoTypeTable type="{ hello: string }" />
```

**Combined**:
```tsx
<AutoTypeTable
  path="file.ts"
  type="A & { world: string }"
/>
```

### Important Notes

- **Server Component only**: Cannot be used in client components
- **Path is relative**: Paths are relative to project directory (cwd), not MDX file location
- **Object types only**: For functions, wrap them in an object type
- **Build-time required**: Must be built at build time, not suitable for serverless runtime

---

## Code Block

**Purpose**: Display syntax-highlighted code blocks with copy button and custom titles.

**Installation**: Built into fumadocs-mdx, works with Rehype Code

### Setup

**mdx-components.tsx**
```tsx
import defaultComponents from 'fumadocs-ui/mdx';
import { CodeBlock, Pre } from 'fumadocs-ui/components/codeblock';

export function getMDXComponents(components?: MDXComponents) {
  return {
    ...defaultComponents,
    pre: ({ ref: _ref, ...props }) => (
      <CodeBlock {...props}>
        <Pre>{props.children}</Pre>
      </CodeBlock>
    ),
    ...components,
  };
}
```

### Features

- Copy button
- Custom titles and icons
- Syntax highlighting via Shiki
- Optional background color

### Keep Background Option

To preserve Shiki's generated background color:

```tsx
<CodeBlock keepBackground {...props}>
  <Pre>{props.children}</Pre>
</CodeBlock>
```

### Custom Icons

Pass an `icon` prop to CodeBlock component.

---

## Files

**Purpose**: Display file structure hierarchies in documentation.

**Installation**: Built into `@fumadocs-ui/components/files`

### Basic Usage

```tsx
import { File, Folder, Files } from 'fumadocs-ui/components/files';

<Files>
  <Folder name="app" defaultOpen>
    <File name="layout.tsx" />
    <File name="page.tsx" />
    <File name="global.css" />
  </Folder>
  <Folder name="components">
    <File name="button.tsx" />
    <File name="tabs.tsx" />
  </Folder>
  <File name="package.json" />
</Files>
```

### Remark Plugin

Enable `remark-mdx-files` for additional syntax:

**source.config.ts**
```tsx
import { remarkMdxFiles } from 'fumadocs-core/mdx-plugins/remark-mdx-files';
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [remarkMdxFiles],
  },
});
```

### Code Block Syntax

Converts files code blocks into `<Files />` component:

\`\`\`files
project
├── src
│   ├── index.js
│   └── utils
│       └── helper.js
├── package.json
\`\`\`

### Auto-Generated Files

Generate from glob pattern:

```tsx
<auto-files dir="./my-dir" pattern="**/*.{ts,tsx}" />
<auto-files dir="./my-dir" pattern="**/*.{ts,tsx}" defaultOpenAll />
```

### Props

**Files**
| Prop | Type | Description |
|------|------|-------------|
| children | `ReactNode` | File and Folder components |

**Folder**
| Prop | Type | Description |
|------|------|-------------|
| name | `string` | Folder display name |
| defaultOpen | `boolean` | Whether folder is expanded by default |

**File**
| Prop | Type | Description |
|------|------|-------------|
| name | `string` | File display name |

---

## GitHub Info

**Purpose**: Display GitHub repository information (owner/repo and star count).

**Installation**: Built into `@fumadocs-ui/components/github-info`

### Basic Usage

```tsx
import { GithubInfo } from 'fumadocs-ui/components/github-info';

<GithubInfo
  owner="fuma-nama"
  repo="fumadocs"
  token={process.env.GITHUB_TOKEN}
/>
```

### Integration with Docs Layout

Add to docs layout links:

**app/docs/layout.tsx**
```tsx
import { DocsLayout } from 'fumadocs-ui/layouts/notebook';
import { source } from '@/lib/source';
import { GithubInfo } from 'fumadocs-ui/components/github-info';

function docsOptions() {
  return {
    tree: source.getPageTree(),
    links: [
      {
        type: 'custom',
        children: <GithubInfo owner="fuma-nama" repo="fumadocs" className="lg:-mx-2" />,
      },
    ],
  };
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <DocsLayout {...docsOptions()}>{children}</DocsLayout>;
}
```

### Props

| Prop | Type | Description |
|------|------|-------------|
| owner | `string` | GitHub repository owner |
| repo | `string` | GitHub repository name |
| token | `string` | Optional GitHub access token for API rate limits |

---

## Inline TOC

**Purpose**: Add inline table of contents to documentation pages.

**Installation**: Built into `@fumadocs-ui/components/inline-toc`

### Usage in MDX

```tsx
import { InlineTOC } from 'fumadocs-ui/components/inline-toc';

<InlineTOC items={toc}>Table of Contents</InlineTOC>
```

### Global Implementation

Add to every page:

**app/docs/[[...slug]]/page.tsx**
```tsx
import { DocsPage } from 'fumadocs-ui/layouts/docs/page';
import { InlineTOC } from 'fumadocs-ui/components/inline-toc';

export default function Page({ page }: { page: Page }) {
  return (
    <DocsPage toc={page.data.toc}>
      <InlineTOC items={page.data.toc}>Table of Contents</InlineTOC>
      {page.content}
    </DocsPage>
  );
}
```

---

## Steps

**Purpose**: Visual step-by-step guides with numbered indicators.

**Installation**: Built into `@fumadocs-ui/components/steps`

### Basic Usage

```tsx
import { Step, Steps } from 'fumadocs-ui/components/steps';

<Steps>
  <Step>
    ### Step 1: Installation

    Install the package...
  </Step>
  <Step>
    ### Step 2: Configuration

    Configure the settings...
  </Step>
</Steps>
```

### Without Imports

Use Tailwind CSS utilities directly:

```tsx
<div className="fd-steps">
  <div className="fd-step">
    ### Step 1
  </div>
  <div className="fd-step">
    ### Step 2
  </div>
</div>
```

### Headings Only

Apply step styles to headings only:

```tsx
<div className='fd-steps [&_h3]:fd-step'>
  <h3>Step 1</h3>
  <p>Some content</p>
  <h3>Step 2</h3>
  <p>More content</p>
</div>
```

---

## Tabs

**Purpose**: Tabbed content with support for persistent and shared values across components.

**Installation**: Built into `@fumadocs-ui/components/tabs`

### Basic Usage

**mdx-components.tsx**
```tsx
import defaultMdxComponents from 'fumadocs-ui/mdx';
import * as TabsComponents from 'fumadocs-ui/components/tabs';

export function getMDXComponents(components?: MDXComponents) {
  return {
    ...defaultMdxComponents,
    ...TabsComponents,
    ...components,
  };
}
```

**In MDX**
```tsx
<Tabs items={['Javascript', 'Rust']}>
  <Tab value="Javascript">Javascript is weird</Tab>
  <Tab value="Rust">Rust is fast</Tab>
</Tabs>
```

### Shared Value

Share tab state across multiple tab groups using `groupId`:

```tsx
<Tabs groupId="language" items={['Javascript', 'Rust']}>
  <Tab value="Javascript">Javascript content</Tab>
  <Tab value="Rust">Rust content</Tab>
</Tabs>
```

### Persistent Tabs

Persist tab selection in localStorage:

```tsx
<Tabs groupId="language" items={['Javascript', 'Rust']} persist>
  <Tab value="Javascript">Javascript</Tab>
  <Tab value="Rust">Rust</Tab>
</Tabs>
```

### Default Value

```tsx
<Tabs items={['Javascript', 'Rust']} defaultIndex={1}>
  <Tab value="Javascript">Javascript</Tab>
  <Tab value="Rust">Rust</Tab>
</Tabs>
```

### Link to Tab

Add HTML `id` attribute for hash-based navigation:

```tsx
<Tabs items={['Javascript', 'Rust', 'C++']}>
  <Tab value="Javascript">Javascript</Tab>
  <Tab value="Rust">Rust</Tab>
  <Tab id="tab-cpp" value="C++">
    C++ content
  </Tab>
</Tabs>
```

Navigate to `#tab-cpp` to open the C++ tab.

### Update URL Hash

Automatically update URL hash when tab changes:

```tsx
<Tabs items={['Javascript', 'Rust']} updateAnchor>
  <Tab id="tab-js" value="Javascript">Javascript</Tab>
  <Tab id="tab-rs" value="Rust">Rust</Tab>
</Tabs>
```

### Advanced Usage

Use primitive Radix UI components:

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from 'fumadocs-ui/components/tabs';

<Tabs defaultValue="npm">
  <TabsList>
    <TabsTrigger value="npm">
      <NpmIcon />
      npm
    </TabsTrigger>
  </TabsList>
  <TabsContent value="npm">Content here</TabsContent>
</Tabs>
```

---

## Type Table

**Purpose**: Document component props and types in a table format.

**Installation**: Built into `@fumadocs-ui/components/type-table`

### Basic Usage

```tsx
import { TypeTable } from 'fumadocs-ui/components/type-table';

<TypeTable
  type={{
    percentage: {
      description: 'The percentage of scroll position',
      type: 'number',
      default: 0.2,
    },
  }}
/>
```

### Props

| Prop | Type | Description |
|------|------|-------------|
| type | `Record<string, { description: string, type: string, default?: any }>` | Type definitions to display |

---

## Callout Component

**Purpose**: Highlight important information, warnings, tips, and errors.

### Usage

```tsx
import { Callout } from 'fumadocs-ui/components/callout';

<Callout type="info" title="Information">
  Important information here.
</Callout>

<Callout type="success" title="Best Practice">
  Recommended approach...
</Callout>

<Callout type="warning" title="Warning">
  Be careful about...
</Callout>

<Callout type="error" title="Common Mistake">
  Don't do this...
</Callout>
```

### Types

- `info`: General information and notes
- `success`: Best practices, recommendations
- `warning`: Warnings, breaking changes, potential issues
- `error`: Common mistakes, dangerous patterns

---

## Cards Component

**Purpose**: Display related content links in a card grid layout.

### Usage

```tsx
import { Cards, Card } from 'fumadocs-ui/components/card';

<Cards>
  <Card
    title="Core Concepts"
    href="/docs/concepts"
    description="Learn about monads, immutability, and type safety"
  />
  <Card
    title="Error Handling Guide"
    href="/docs/guides/error-handling"
    description="Master error handling strategies"
  />
  <Card
    title="Best Practices"
    href="/docs/best-practices"
    description="Write better functional code"
  />
</Cards>
```

---

## Best Practices

### When to Use Each Component

| Component | Use Case |
|-----------|----------|
| **Accordion** | FAQs, optional details, collapsible sections |
| **Auto Type Table** | API documentation, TypeScript type references |
| **Code Block** | All code examples with syntax highlighting |
| **Files** | Project structure, file organization examples |
| **GitHub Info** | Repository info in sidebar/header |
| **Inline TOC** | Long-form content, multi-section pages |
| **Steps** | Tutorials, setup guides, sequential instructions |
| **Tabs** | Alternative solutions, multiple language examples |
| **Type Table** | Component props, configuration options |
| **Callout** | Important notes, warnings, tips |
| **Cards** | Related content, next steps navigation |

### Performance Considerations

- **Auto Type Table**: Requires TypeScript compiler, use sparingly
- **Code Block**: Pre-rendered at build time for optimal performance
- **GitHub Info**: Consider caching GitHub API responses
- **Tabs with persistence**: Uses localStorage, minimal performance impact

### Accessibility

All components follow WCAG guidelines:
- Keyboard navigation support
- ARIA labels and roles
- Screen reader compatible
- Focus indicators

---

## Resources

- [Fumadocs UI Documentation](https://fumadocs-ui.vercel.app/)
- [Fumadocs Core](https://fumadocs.dev/)
- [Radix UI](https://www.radix-ui.com/) - Underlying component library
- [Base UI](https://base.ui.com/) - Alternative component foundation

---

## Migration Notes

When updating fumadocs components, check:
- Breaking changes in props API
- Changes in default behavior
- New features or deprecations
- Performance improvements

Always test documentation builds after component updates.
