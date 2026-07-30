import { Dialog as HeadlessDialog, Transition } from "@headlessui/react";
import React, { Fragment } from "react";

interface Props {
  open: boolean;
  setOpen: (open: boolean) => void;
  title?: string;
  children?: React.ReactNode;
  actions?: React.ReactNode;
  inline?: boolean;
}

const Dialog = ({ open, setOpen, title, children, actions }: Props) => {
  return (
    <Transition appear show={open} as={Fragment}>
      <HeadlessDialog as="div" className="relative z-50" onClose={() => setOpen(false)}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <HeadlessDialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-slate-1 p-6 text-left align-middle shadow-depth-2 transition-all">
                {title && (
                  <HeadlessDialog.Title
                    as="h3"
                    className="text-lg font-bold leading-6 text-slate-12"
                  >
                    {title}
                  </HeadlessDialog.Title>
                )}
                <div className="mt-4 text-sm text-slate-11">{children}</div>
                {actions && <div className="mt-6 flex gap-3">{actions}</div>}
              </HeadlessDialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </HeadlessDialog>
    </Transition>
  );
};

export default Dialog;
