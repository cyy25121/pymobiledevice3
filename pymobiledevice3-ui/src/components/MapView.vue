<template>
  <div class="mapview">
    <h1>最好玩的萌夯步行遊戲</h1>
    <el-row
      el-row
      justify="center"
      align="middle"
      type="flex"
      style="margin: 30px"
    >
      <el-col :span="5">
        <el-input
          placeholder="請輸入 Host port (ex: fd69:e04:ca67::1 53777)"
          prefix-icon="el-icon-search"
          v-model="rsd"
        >
        </el-input>
      </el-col>
      <el-col :span="3">
        <el-button type="primary" @click="setRSD" :loading="loading"
          >設定RSD</el-button
        >
      </el-col>
      <el-col :span="5">
        <el-statistic title="現在座標"
          ><template slot="formatter">{{ loc }}</template>
        </el-statistic>
      </el-col>
      <el-col :span="3">
        <el-button type="primary" @click="getUserLocation" :loading="loading"
          >取得目前位置</el-button
        >
      </el-col>
    </el-row>

    <div id="map"></div>
  </div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import axios from "axios";

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

export default {
  name: "MapView",
  props: {
    msg: String,
  },
  data() {
    return {
      currentPosition: {
        latitude: 0,
        longitude: 0,
      },
      loading: false,
      map: null,
      marker: null,
      rsd: "",
    };
  },
  methods: {
    setRSD() {
      axios
        .get(
          `http://localhost:3000/setting?rsd=${this.rsd}&lat=${this.currentPosition.latitude}&lng=${this.currentPosition.longitude}`,
          {
            headers: {
              "Access-Control-Allow-Origin": "*",
            },
          }
        )
        .then((response) => {
          console.log(response);
          this.$message({
            message: response.data,
            type: "success",
          });
        })
        .catch((error) => {
          console.log(error);
          this.$message({
            message: "發生錯誤",
            type: "error",
          });
        });
    },
    getUserLocation() {
      if (navigator.geolocation) {
        this.loading = true;
        navigator.geolocation.getCurrentPosition(
          (position) => {
            this.currentPosition = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            };
            if (this.map === null) {
              this.map = L.map("map", {
                center: [
                  this.currentPosition.latitude,
                  this.currentPosition.longitude,
                ],
                zoom: 15,
              });
              L.tileLayer(
                "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                {
                  attribution:
                    'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
                  maxZoom: 18,
                }
              ).addTo(this.map);
              this.map.on("click", (e) => {
                this.currentPosition = {
                  latitude: e.latlng.lat,
                  longitude: e.latlng.lng,
                };
                // 加入新的 marker前，先移除舊的 marker
                if (this.marker !== null) {
                  this.map.removeLayer(this.marker);
                }

                this.marker = L.marker([e.latlng.lat, e.latlng.lng], {
                  opacity: 1.0,
                }).addTo(this.map);

                axios
                  .get(
                    `http://localhost:3000/location?lat=${this.currentPosition.latitude}&lng=${this.currentPosition.longitude}`,
                    {
                      headers: {
                        "Access-Control-Allow-Origin": "*",
                      },
                    }
                  )
                  .then((response) => {
                    console.log(response);
                    this.$message({
                      message: response.data,
                      type: "success",
                    });
                  })
                  .catch((error) => {
                    console.log(error);
                    this.$message({
                      message: "發生錯誤",
                      type: "error",
                    });
                  });
              });
            } else {
              this.map.setView(
                [this.currentPosition.latitude, this.currentPosition.longitude],
                15
              );
            }
            this.marker = L.marker(
              [this.currentPosition.latitude, this.currentPosition.longitude],
              {
                opacity: 1.0,
              }
            ).addTo(this.map);

            this.loading = false;
          },
          () => {
            this.$message({
              message: "目前無法取得您的位置",
              type: "error",
            });
          }
        );
      } else {
        this.$message({
          message: "瀏覽器目前無法取得您的位置",
          type: "error",
        });
      }
    },
  },
  mounted() {
    this.getUserLocation();
  },
  computed: {
    loc() {
      return this.currentPosition.latitude === 0 &&
        this.currentPosition.longitude === 0
        ? "-"
        : `${this.currentPosition.latitude}, ${this.currentPosition.longitude}`;
    },
  },
};
</script>

<style scoped>
#map {
  height: 500px;
  width: 80%;
  margin-left: auto;
  margin-right: auto;
}
</style>
