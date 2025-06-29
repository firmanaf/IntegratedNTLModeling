"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
Nighttime Light Modeller: pixel-wise forecasting with model options, NoData handling, R² & RMSE logging, optional normalization, and scatter plot visualization.
Created by Firman Afrianto during PT. Sagamartha Ultima SkillShare 2025.
"""
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterString,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterEnum,
    QgsRasterLayer,
    QgsProject
)
import numpy as np
import os
import rasterio
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures, MinMaxScaler, StandardScaler

class NighttimeLightModeller(QgsProcessingAlgorithm):
    LAYER_LIST = 'LAYER_LIST'
    FUTURE_YEARS = 'FUTURE_YEARS'
    MODEL_TYPE = 'MODEL_TYPE'
    NORMALIZATION = 'NORMALIZATION'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'

    def tr(self, string):
        return QCoreApplication.translate('NighttimeLightModeller', string)

    def createInstance(self):
        return NighttimeLightModeller()

    def name(self):
        return 'nighttimelightmodeller'

    def displayName(self):
        return self.tr('Nighttime Light Regression Modeler')

    def shortHelpString(self):
        return self.tr(
            'Forecast pixel-wise Nighttime Light (NTL) using multiple regression models, optional normalization, ' \
            'with NoData handling, R² & RMSE reporting, and scatter plot visualization.\n'
            'Created by Firman Afrianto during PT. SAGAMARTHA ULTIMA SkillShare 2025.'
        )

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.LAYER_LIST,
                self.tr('Select input NTL rasters (2013–2023)'),
                layerType=QgsProcessing.TypeRaster
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.FUTURE_YEARS,
                self.tr('Future years (comma-separated)'),
                defaultValue='2028,2033,2038,2043'
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.MODEL_TYPE,
                self.tr('Select regression model'),
                options=['Linear','Polynomial (degree 2)','Ridge','Lasso'],
                defaultValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.NORMALIZATION,
                self.tr('Select normalization method'),
                options=['None','MinMax','Z-score'],
                defaultValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                self.tr('Select output folder')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Read input rasters
        layers = self.parameterAsLayerList(parameters, self.LAYER_LIST, context)
        paths = [lyr.dataProvider().dataSourceUri() for lyr in layers if lyr and lyr.isValid()]
        if len(paths) < 2:
            raise QgsProcessingException(self.tr('Please select at least 2 input rasters.'))

        # Parse future years
        fy_str = self.parameterAsString(parameters, self.FUTURE_YEARS, context)
        future_years = np.array([int(x) for x in fy_str.split(',') if x.strip().isdigit()]).reshape(-1,1)
        if future_years.size == 0:
            raise QgsProcessingException(self.tr('No valid future years provided.'))

        # Model and normalization settings
        model_name = ['Linear','Polynomial','Ridge','Lasso'][self.parameterAsEnum(parameters, self.MODEL_TYPE, context)]
        norm_name = ['None','MinMax','Z-score'][self.parameterAsEnum(parameters, self.NORMALIZATION, context)]

        # Load rasters
        with rasterio.Env():
            with rasterio.open(paths[0]) as src:
                profile = src.profile
                nodata_val = src.nodata
            arrays = [rasterio.open(p).read(1) for p in paths]
        data = np.stack(arrays, axis=0)
        years = np.arange(2013, 2013 + len(paths)).reshape(-1,1)
        H, W = data.shape[1:]

        # Mask NoData
        valid_mask = ~np.any(data == nodata_val, axis=0) if nodata_val is not None else np.ones((H,W),bool)

        flat = data.reshape(len(paths), -1)
        n_pixels, n_future = H*W, future_years.shape[0]
        preds = np.zeros((n_future, n_pixels),dtype=np.float32)
        r2_vals = np.full(n_pixels,np.nan,dtype=np.float32)
        rmse_vals = np.full(n_pixels,np.nan,dtype=np.float32)

        # Prepare polynomial features if needed
        if model_name=='Polynomial':
            poly = PolynomialFeatures(degree=2)
            years_feat = poly.fit_transform(years)
            future_feat = poly.transform(future_years)
        else:
            years_feat, future_feat = years, future_years

        feedback.pushInfo(self.tr(f'Starting regression (model={model_name}, norm={norm_name})...'))
        for idx in range(n_pixels):
            if feedback.isCanceled(): break
            if not valid_mask.flat[idx]: continue
            y = flat[:,idx].reshape(-1,1)
            # Normalize
            if norm_name=='MinMax':
                scaler = MinMaxScaler()
                y_norm = scaler.fit_transform(y)
            elif norm_name=='Z-score':
                scaler = StandardScaler()
                y_norm = scaler.fit_transform(y)
            else:
                scaler = None
                y_norm = y
            # Select model
            mdl = {'Linear':LinearRegression(),
                   'Polynomial':LinearRegression(),
                   'Ridge':Ridge(),
                   'Lasso':Lasso()}[model_name]
            mdl.fit(years_feat,y_norm)
            # Predictions
            y_pred_norm = mdl.predict(years_feat).reshape(-1,1)
            y_pred = scaler.inverse_transform(y_pred_norm) if scaler else y_pred_norm
            pred_norm = mdl.predict(future_feat).reshape(-1,1)
            pred = scaler.inverse_transform(pred_norm).flatten() if scaler else pred_norm.flatten()
            preds[:,idx] = pred
            # Metrics
            r2_vals[idx] = mdl.score(years_feat,y_norm)
            resid = y_pred.flatten() - y.flatten()
            rmse_vals[idx] = np.sqrt(np.mean(resid**2))
            if idx % max(1,n_pixels//100)==0:
                feedback.setProgress(int(idx/n_pixels*100))

        # Clip results
        preds = np.maximum(preds,0).reshape((n_future,H,W))

        # Prepare output folder
        out_folder = self.parameterAsString(parameters,self.OUTPUT_FOLDER,context)
        os.makedirs(out_folder,exist_ok=True)
        profile.update(count=1,dtype='float32')

        # Log metrics
        vr2 = r2_vals[~np.isnan(r2_vals)]
        vrm = rmse_vals[~np.isnan(rmse_vals)]
        feedback.pushInfo(f"R² - mean:{vr2.mean():.3f},min:{vr2.min():.3f},max:{vr2.max():.3f}")
        feedback.pushInfo(f"RMSE - mean:{vrm.mean():.3f},min:{vrm.min():.3f},max:{vrm.max():.3f}")
        robust_pct = 100 * np.sum(vr2>=0.7) / vr2.size
        feedback.pushInfo(f"Robust(R²>=0.7):{robust_pct:.1f}%")

        # Scatter plot actual vs predicted for first future year
        actual = data[-1].flatten()[valid_mask.flatten()]
        predicted = preds[0].flatten()[valid_mask.flatten()]
        sample_size = min(10000,len(actual))
        idxs = np.random.choice(len(actual),sample_size,replace=False)
        plt.figure()
        plt.scatter(actual[idxs],predicted[idxs],s=1)
        plt.xlabel('Actual NTL')
        plt.ylabel(f'Predicted NTL ({future_years.flatten()[0]})')
        plt.title('Actual vs Predicted NTL')
        scatter_path = os.path.join(out_folder,'scatter_actual_vs_predicted.png')
        plt.savefig(scatter_path)
        plt.close()
        feedback.pushInfo(f"Scatter plot saved: {scatter_path}")

        # Save predicted rasters
        results = {}
        for i,yr in enumerate(future_years.flatten()):
            out_path = os.path.join(out_folder,f'NTL_Pred_{yr}.tif')
            with rasterio.open(out_path,'w',**profile) as dst:
                dst.write(preds[i],1)
            layer = QgsRasterLayer(out_path,f'NTL Prediction {yr}')
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
            results[str(yr)] = out_path

        feedback.pushInfo(self.tr('Processing complete; layers have been added.'))
        return results
