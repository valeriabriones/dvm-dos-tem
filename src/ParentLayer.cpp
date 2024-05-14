/*! \file
 *
 */
#include "../include/ParentLayer.h"

#include "../include/TEMLogger.h"
extern src::severity_logger< severity_level > glg;

ParentLayer::ParentLayer(const double & thick) {
  BOOST_LOG_SEV(glg, debug) << "==> Creating a ParentLayer object...";
  tkey=I_ROCK;
  isRock = true;
  solind = MISSING_I;
  dz = thick;
  updateProperty();
};

ParentLayer::~ParentLayer() {
  BOOST_LOG_SEV(glg, debug) << "--> Deleting a ParentLayer object...";
};

void ParentLayer::updateProperty() {
  poro =  0;
  tcsolid =2;//
  tcsatunf= tcsolid;
  tcsatfrz= tcsolid;
  vhcsolid = 2700000;
};

// get frozen layer specific heat capcity
double ParentLayer::getFrzVolHeatCapa() {
  return vhcsolid;
};

double ParentLayer::getUnfVolHeatCapa() {
  return vhcsolid;
};

double ParentLayer::getMixVolHeatCapa() {
  return vhcsolid;
};

// get frozen layer thermal conductivity
double ParentLayer::getFrzThermCond() {
  return tcsolid;
};

// get unfrozen layer thermal conductivity
double ParentLayer::getUnfThermCond() {
  return tcsolid;
};

// get albedo of visible radiation
double ParentLayer::getAlbedoVis() { //should not used
  double vis=0.2;
  return vis;
};

// get albedo of nir radiation
double ParentLayer::getAlbedoNir() { //should not used
  double nir=0.2;
  return nir;
};

