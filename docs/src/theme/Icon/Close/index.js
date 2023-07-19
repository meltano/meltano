import React from "react";
export default function IconClose({
  width = 40,
  height = 40,
  color = "currentColor",
  strokeWidth = 2,
  className,
  ...restProps
}) {
  return (
    <svg viewBox="0 0 28 19" width={width} height={height} {...restProps}>
      <g>
        <path
          id="Vector 1"
          d="M23 17.5L7 1.5"
          stroke={color}
          strokeWidth={strokeWidth}
        />
        <path
          id="Vector 3"
          d="M23 1.5L7 17.5"
          stroke={color}
          strokeWidth={strokeWidth}
        />
      </g>
    </svg>
  );
}
