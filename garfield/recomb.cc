/**
 * recomb.cc
 *
 * Generates electron tracks in xenon gas and outputs them to text files.
 *
*/
#include <iostream>
#include <cmath>
#include <cstring>
#include <fstream>
#include <TCanvas.h>
#include <TApplication.h>
#include <TFile.h>

#include "MediumMagboltz.hh"
#include "ComponentElmer.hh"
#include "Sensor.hh"
#include "ViewField.hh"
#include "Plotting.hh"
#include "ViewFEMesh.hh"
#include "ViewSignal.hh"
#include "GarfieldConstants.hh"
#include "Random.hh"
#include "AvalancheMicroscopic.hh"
#include "SolidBox.hh"
#include "GeometrySimple.hh"
#include "ComponentConstant.hh"

using namespace Garfield;

int main(int argc, char * argv[]) {

    TApplication app("app", &argc, argv);

    const double vol_side = 100.;         // side length of cubical volume
    const int nelectrons = 1000;            // total number of electrons
    const double elec_energy = 662000;  // electron energy in eV

    // ---------------------------------------------------------------------------------------------------------------
    // Create several canvases for the plots.
    //TCanvas * cGeom = new TCanvas("geom","Geometry/Avalanche/Fields");
    //TCanvas * cSignal = new TCanvas("signal","Signal");

    // Define the medium.
    MediumMagboltz* gas = new MediumMagboltz();
    gas->SetTemperature(293.15);                  // Set the temperature (K)
    gas->SetPressure(7500.);                       // Set the pressure (Torr)
    gas->EnableDrift();                           // Allow for drifting in this medium
    gas->SetComposition("xe", 100.);   // Specify the gas mixture

    GeometrySimple* geo = new GeometrySimple();
    SolidBox* box = new SolidBox(0., 0., 0., vol_side, vol_side, vol_side);
    geo->AddSolid(box, gas);

    // Set up a constant electric field.
    ComponentConstant* cmp = new ComponentConstant();
    cmp->SetGeometry(geo);
    cmp->SetElectricField(0., 0., 0.);

    Sensor* sensor = new Sensor();
    sensor->AddComponent(cmp);

    // Create an avalanche object.
    AvalancheMicroscopic* aval = new AvalancheMicroscopic();
    aval->SetSensor(sensor);
    aval->SetCollisionSteps(100);
    aval->SetElectronTransportCut(10);
    //aval->EnableSignalCalculation();
    //aval->SetUserHandleInelastic(hd_inelastic);
    //aval->SetUserHandleStep(hd_step);

    // Calculate the avalanche.
    for (int i = 0; i < nelectrons; i++) {

        // Set the electron start parameters.
        double xi = 0;
        double yi = 0;
        double zi = 0;

        std::cout << "[Avalanche " << i << " of " << nelectrons << "] from ("
                  << xi << ", " << yi << ", " << zi << ") ... ";
        aval->AvalancheElectron(xi, yi, zi, 0., elec_energy, 0., 1., 0.);

        int ne_tot = aval->GetNumberOfElectronEndpoints();
        char fname[20];
        sprintf(fname, "tracks/electron_%d.dat",i);
        std::ofstream ofile(fname);
        ofile << "# x0 y0 z0 t0 e0 x1 y1 z1 t1 e1 status" << std::endl;
        for(int ne = 0; ne < ne_tot; ne++) {

            // For obtaining the endpoint:
            double x0, y0, z0, t0, e0, x1, y1, z1, t1, e1;
            int status;

            // Get the endpoint and write the information to file.
            aval->GetElectronEndpoint(ne,x0,y0,z0,t0,e0,x1,y1,z1,t1,e1,status);
            ofile << x0 << " " << y0 << " " << z0 << " " << t0 << " " << e0
                  << " " << x1 << " " << y1 << " " << z1 << " " << t1 << " "
                  << e1 << " " << status << std::endl;

        }
        ofile.close();
        std::cout << " written to file." << std::endl;
    }
    std::cout << "Done." << std::endl;

    // ---------------------------------------------------------------------------------------------------------------

    app.Run(kTRUE);

    return 0;
}
