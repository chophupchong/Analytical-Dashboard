const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  devServer: {
    proxy: {
      target: 'https://chc-api.onrender.com/',
      changeOrigin: true,
      secure: false,
    },
  },
});
