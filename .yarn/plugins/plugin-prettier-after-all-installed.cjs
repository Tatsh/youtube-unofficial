/* eslint-disable */
//prettier-ignore
module.exports = {
name: "@yarnpkg/plugin-prettier-after-all-installed",
factory: function (require) {
"use strict";
var plugin = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __require = /* @__PURE__ */ ((x) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(x, {
    get: (a, b) => (typeof require !== "undefined" ? require : a)[b]
  }) : x)(function(x) {
    if (typeof require !== "undefined")
      return require.apply(this, arguments);
    throw new Error('Dynamic require of "' + x + '" is not supported');
  });
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // index.ts
  var yarnpkg_plugin_prettier_after_all_installed_exports = {};
  __export(yarnpkg_plugin_prettier_after_all_installed_exports, {
    default: () => yarnpkg_plugin_prettier_after_all_installed_default
  });
  var import_core = __require("@yarnpkg/core");
  var import_process = __require("process");
  var import_cli = __require("@yarnpkg/cli");
  var plugin = {
    hooks: {
      afterAllInstalled(project) {
        void (async () => {
          const cwd = (0, import_process.cwd)();
          const configuration = await import_core.Configuration.find(cwd, (0, import_cli.getPluginConfiguration)());
          const { locator } = await import_core.Project.find(configuration, cwd);
          const packageAccessibleBinaries = await import_core.scriptUtils.getPackageAccessibleBinaries(locator, {
            project
          });
          if (!packageAccessibleBinaries.get("prettier")) {
            throw new Error("Prettier not found.");
          }
          const ret = await import_core.scriptUtils.executePackageAccessibleBinary(
            locator,
            "prettier",
            ["--log-level", "error", "-w", "package.json", ".yarnrc.yml"],
            { cwd, packageAccessibleBinaries, project, stderr: import_process.stderr, stdin: import_process.stdin, stdout: import_process.stdout }
          );
          if (ret !== 0) {
            throw new Error(`Prettier returned non-zero: ${ret}.`);
          }
        })();
      }
    }
  };
  var yarnpkg_plugin_prettier_after_all_installed_default = plugin;
  return __toCommonJS(yarnpkg_plugin_prettier_after_all_installed_exports);
})();
return plugin;
}
};
