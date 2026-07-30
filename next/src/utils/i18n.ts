import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import commonEn from "../../public/locales/en/common.json";
import commonZh from "../../public/locales/zh/common.json";
import commonZhtw from "../../public/locales/zhtw/common.json";
import indexPageEn from "../../public/locales/en/indexPage.json";
import indexPageZh from "../../public/locales/zh/indexPage.json";
import indexPageZhtw from "../../public/locales/zhtw/indexPage.json";
import settingsEn from "../../public/locales/en/settings.json";
import settingsZh from "../../public/locales/zh/settings.json";
import settingsZhtw from "../../public/locales/zhtw/settings.json";
import helpEn from "../../public/locales/en/help.json";
import helpZh from "../../public/locales/zh/help.json";
import helpZhtw from "../../public/locales/zhtw/help.json";
import errorsEn from "../../public/locales/en/errors.json";
import errorsZh from "../../public/locales/zh/errors.json";
import errorsZhtw from "../../public/locales/zhtw/errors.json";
import drawerEn from "../../public/locales/en/drawer.json";
import drawerZh from "../../public/locales/zh/drawer.json";
import drawerZhtw from "../../public/locales/zhtw/drawer.json";
import chatEn from "../../public/locales/en/chat.json";
import chatZh from "../../public/locales/zh/chat.json";
import chatZhtw from "../../public/locales/zhtw/chat.json";
import languagesEn from "../../public/locales/en/languages.json";
import languagesZh from "../../public/locales/zh/languages.json";
import languagesZhtw from "../../public/locales/zhtw/languages.json";

const resources = {
  en: {
    common: commonEn,
    indexPage: indexPageEn,
    settings: settingsEn,
    help: helpEn,
    errors: errorsEn,
    drawer: drawerEn,
    chat: chatEn,
    languages: languagesEn,
  },
  zh: {
    common: commonZh,
    indexPage: indexPageZh,
    settings: settingsZh,
    help: helpZh,
    errors: errorsZh,
    drawer: drawerZh,
    chat: chatZh,
    languages: languagesZh,
  },
  zhtw: {
    common: commonZhtw,
    indexPage: indexPageZhtw,
    settings: settingsZhtw,
    help: helpZhtw,
    errors: errorsZhtw,
    drawer: drawerZhtw,
    chat: chatZhtw,
    languages: languagesZhtw,
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "en",
  fallbackLng: "en",
  defaultNS: "common",
  ns: ["common", "help", "settings", "chat", "errors", "languages", "drawer", "indexPage"],
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
