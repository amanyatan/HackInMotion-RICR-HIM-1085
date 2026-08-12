declare module '*.css' {
  const content: { [key: string]: string };
  export default content;
}

declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.splinecode' {
  const content: string;
  export default content;
}
