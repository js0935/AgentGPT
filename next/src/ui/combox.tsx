import clsx from "clsx";
import React from "react";

interface ComboProps<T> {
  label: string;
  value: T;
  valueMapper: (item: T) => string;
  onChange: (item: T) => void;
  items: T[];
  icon?: React.ReactNode;
}

const Combo = <T,>(props: ComboProps<T>) => {
  const selectedIndex = props.items.findIndex(
    (item) => props.valueMapper(item) === props.valueMapper(props.value)
  );

  return (
    <div>
      {props.label && (
        <label className="flex items-center gap-2 text-sm font-bold leading-6 text-slate-12">
          {props.icon}
          <span>{props.label}</span>
        </label>
      )}
      <div className="relative flex flex-col gap-1 rounded-md shadow-sm">
        <select
          className={clsx(
            "placeholder:text-color-tertiary focus:outline-inset block w-full rounded-md border-0 bg-slate-1 p-1.5 text-slate-12 shadow-depth-1 transition-colors sm:text-sm sm:leading-6"
          )}
          value={selectedIndex}
          onChange={(e) => {
            const idx = parseInt(e.target.value, 10);
            if (idx >= 0 && idx < props.items.length) {
              props.onChange(props.items[idx]);
            }
          }}
        >
          {props.items.map((item, index) => (
            <option key={index} value={index}>
              {props.valueMapper(item)}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default Combo;
