<script setup>
import axios from "axios";
import { ref} from "vue";

const prompt_input = ref("");
const prompts = ref([]);

function send_prompt(evt){
  const prompt_input = evt.target.value;
  let index = prompts.value.length;
  prompts.value.push({
    "action": "",
    "prompt": prompt_input,
    "loading": true,
    "output": null
  });
  axios.get(`http://localhost:7080/?prompt=${prompt_input}`).then((response)=>{
    const result = response.data;
    prompts.value[index]["output"] = result.data;
    prompts.value[index]["action"] = result.action;
    prompts.value[index]["loading"] = false;  
  }).catch((error) => {
    console.error(error);
    prompts.value[index]["loading"] = false;
    alert("an error occured.");
  })
}

</script>

<template>
  <div id="chat-container">
    <div align="center">
      <svg xmlns="http://www.w3.org/2000/svg" width="92" height="92" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bot-icon lucide-bot"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
      <h3 style="margin-bottom:2px;font-size:24pt;padding:0px;margin:0px;">
        Hello! Im you Network Agent
      </h3>
    </div>
    <div id="prompts">
      <div class="prompt-item" v-for="(item,key) in prompts" :key="key">
        <div class="prompt-user">
          {{  item.prompt }}
        </div>
        <div style="clear:both"></div>
        <div class="prompt-output" >
          <div v-if="!item.loading">
            <template v-if="item.action == 'collect'">
              <pre v-for="(log,lkey) in item.output" :key="lkey">{{ log.raw }}</pre>
            </template>
            <template v-else-if="item.action == 'configure-interface-description'">
              <pre>{{item.output}}</pre>
            </template>
          </div>
          <div v-if="item.loading">Loading...</div>
        </div>
        <div style="clear:both"></div>
      </div>
    </div>
    <div>
      <input type="text" @keypress.enter="send_prompt" id="prompt-input" placeholder="How can I help you?"/>
    </div>
  </div>
</template>

<style scoped>
.prompt-item {
  margin-bottom:20px;
}
.prompt-item .prompt-user{
  border:3px solid #cecece;
  width:auto;
  float:right;
  text-align: right;
  padding:20px !important;
  padding-right:20px;
  border-radius: 40px;
  border-top-right-radius: 0px;
  height: fit-content !important;
}
.prompt-item .prompt-output{
  border:3px solid #cecece;
  background-color: #323232;
  width:auto;
  float:left;
  text-align: left;
  margin-top:20px;
  padding:20px !important;
  padding-right:20px;
  border-radius: 40px;
  border-bottom-left-radius: 0px;
  height: fit-content !important;
}
#prompts{
  height:96%;
  border-radius: 12px;
  overflow-y: auto;
  padding:20px;
  margin-bottom:10px;
  border:1px solid #cecece;
}
#prompt-input{
  padding:10px;
  border-radius: 8px;
  width:100%;
  border:3px solid #4b4b4b;
}
body {
  width:100%;
}
#chat-container {
  width:800px;
  height:80vh;
  padding:20px;
  color:#fff;
  border-radius: 10px;
  margin-top:10px;
  margin-left:auto;
  margin-right:auto;
}
</style>
