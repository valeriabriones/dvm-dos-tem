
/*!\file
 * Implementation of Richard's law for soil water dynamics*/

#ifndef RICHARDS_H_
#define RICHARDS_H_

#include <cmath>
#include <limits>

#include "CohortData.h"
#include "EnvData.h"

#include "Layer.h"
#include "SoilLayer.h"
#include "CrankNicholson.h"

class Richards {
public :
  Richards();
  ~Richards();

  int itsum;

  int indx0sl; // first soil layer index applied for Richards Equation
  int indx0al; // active layers' first layer index
  int numal;   // active layers' layer numbers
  double qdrain; // mm/day

  void update(Layer *fstsoill, Layer* bdrainl, const double & bdraindepth,
              const double & fbaseflow, double trans[MAX_SOI_LAY],
              const double & evap, const double & infil, const double &ts);

  void setCohortData(CohortData* cdp);
  void setEnvData(EnvData* edp);

  CrankNicholson cn;

private:

  //void prepareSoilNodes(Layer *currsoill, const double & draindepth);
  void prepareSoilColumn(Layer *currsoill, const double & draindepth);
  void clearRichardsArrays();

  void iterate(const double trans[], const double & evap,
               const double & infil, const double & fbaseflow);
  int updateOnethTimeStep(const double &fbaseflow);
  int updateOneIteration(const double &fbaseflow);

  Layer * drainl;

  double qinfil;
  double qevap;

  //+1, is for easily match-up of soil layer index (starting from 1 in 'ground')
  double qtrans[MAX_SOI_LAY+1];


  //CLM4.5 conversion attempt
  //Incoming values. These already exist in the layers, and are
  // copied to arrays simply so that the equations in Richards
  // are easily comparable to the CLM paper.
  double Bsw[MAX_SOI_LAY+1]; //bsw hornberger constant (by horizon type)
  double k[MAX_SOI_LAY+1]; //Hydraulic conductivity
  double ksat[MAX_SOI_LAY+1]; //Saturated hydraulic conductivity
  double psisat[MAX_SOI_LAY+1];

  //Beginning calculated values
  double psi[MAX_SOI_LAY+1]; //Soil matric potential (mm)
  double psiE[MAX_SOI_LAY+1]; //Equilibrium soil matric potential
  double theta[MAX_SOI_LAY+1];
  double thetasat[MAX_SOI_LAY+1];
  double z_h[MAX_SOI_LAY+1]; //Depth of layer bottom in mm???


  double deltapsi[MAX_SOI_LAY+1];
  double deltatheta_liq[MAX_SOI_LAY+1];
  double deltak[MAX_SOI_LAY+1];
  double thetaE[MAX_SOI_LAY+1]; //Layer-average equilibrium volumetric water content

  //Intermediate calculated values
  double eq7121[MAX_SOI_LAY+1];
  double eq7122[MAX_SOI_LAY+1];
  double eq7123[MAX_SOI_LAY+1];
  double eq7124[MAX_SOI_LAY+1];
  double eq7125[MAX_SOI_LAY+1];

  double eq7117[MAX_SOI_LAY+1]; //Results from equation 7.117
  double eq7118[MAX_SOI_LAY+1]; //Results from equation 7.118
  double eq7119[MAX_SOI_LAY+1]; //Results from equation 7.119
  double eq7120[MAX_SOI_LAY+1]; //Results from equation 7.120

  double coeffA[MAX_SOI_LAY+1]; //Coefficient A for tridiagonal calculation
  double coeffB[MAX_SOI_LAY+1]; //Coefficient B for tridiagonal calculation
  double coeffC[MAX_SOI_LAY+1]; //Coefficient C for tridiagonal calculation
  double coeffR[MAX_SOI_LAY+1]; //Coefficient R for tridiagonal calculation
  double [MAX_SOI_LAY+1]; //Results from tridiagonal calculation



  // var[0] will not used here
  double dzmm[MAX_SOI_LAY+1];      // layer thickness in mm
  double zmm[MAX_SOI_LAY+1];       // layer center of thawed depth in mm
  double laybotmm[MAX_SOI_LAY+1];        // depth of layer bottom in mm
  double nodemm[MAX_SOI_LAY+1];       // in mm
  double effporo[MAX_SOI_LAY+1];   //effective porosity (minus minliq volume)
  double effliq[MAX_SOI_LAY+1];
  double effminliq[MAX_SOI_LAY+1];
  double effmaxliq[MAX_SOI_LAY+1];

  //double hk[MAX_SOI_LAY+1];
  double dhkdw[MAX_SOI_LAY+1];
  double smp[MAX_SOI_LAY+1];
  double dsmpdw[MAX_SOI_LAY+1];
  double qin[MAX_SOI_LAY+1];
  double qout[MAX_SOI_LAY+1];

  //double liqii[MAX_SOI_LAY+1];
  //double liqit[MAX_SOI_LAY+1];
  //double liqis[MAX_SOI_LAY+1];
  //double liqid[MAX_SOI_LAY+1];
  //double liqld[MAX_SOI_LAY+1];

  double amx[MAX_SOI_LAY+1];
  double bmx[MAX_SOI_LAY+1];
  double cmx[MAX_SOI_LAY+1];
  double rmx[MAX_SOI_LAY+1];
  double dwat[MAX_SOI_LAY+1];

  double timestep;  // one timestep in seconds
  double tleft; // the amount of time left for update (fraction of one timestep)

  bool tschanged; //whether the time step has been changed for
                  //  last factional time step
  double tstep;     // actual fraction of one timestep for iteration
  double LIQTOLE;   // tolerance of difference
  double TSTEPMIN;  // min. fraction of one timestep
  double TSTEPMAX;  // max. fraction of one timestep
  double TSTEPORG;  // the original time step

  double mindzlay; //min. layer thickness (meters) for stable Richards' solution


};

#endif /*RICHARDS_H_*/
